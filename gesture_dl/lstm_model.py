import torch
from torch import nn

import itertools
import csv
from collections import deque

from gesture_dl.data.HandTrackingModule import extract_and_normlize

class SequenceClassification(nn.Module):
    def __init__(self, lstm_input_size=512, input_size=73, num_classes=8):
        super().__init__()

        self.batch_norm = nn.BatchNorm1d(num_features=input_size)
        self.dropout = nn.Dropout(p=0.2)

        self.proj = nn.Linear(in_features=input_size, out_features=lstm_input_size)

        self.encoder = nn.LSTM(input_size=lstm_input_size, 
                            hidden_size=lstm_input_size//2,
                            num_layers=2,
                            batch_first=True,
                            dropout=0.1,
                            bidirectional=True
                            )
        
        self.head_norm = nn.LayerNorm(lstm_input_size)
        self.mlp_head = nn.Linear(lstm_input_size, num_classes)

    def norm(self, x):
        x = x.transpose(1, 2)
        x = self.batch_norm(x)
        return x.transpose(1, 2)
    
    def transform(self, x):
        rep, _ = self.encoder(x)
        input_max, input_max_indices = torch.max(rep, dim=1) # max pooling
        return input_max

    def forward(self, batch):
        x = self.dropout(batch)
        x = self.norm(x)
        x = self.proj(x)
        x = self.head_norm(self.transform(x))
        x = self.mlp_head(x)
        return x
    
    def softmax_pred(self, x):
        x = self(x)
        # print(x)
        # print(x.exp())
        # return torch.nn.functional.softmax(x, dim=1)
        return x

class SequenceClassificationPred:
    def __init__(self, model_path, max_sequence_len=60, gesture_name_map=None):
        # load model according to device
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.model = SequenceClassification()
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        # frame fixed len
        self.max_seq_len = max_sequence_len
        self.queue = deque(maxlen=max_sequence_len)
        # frame stack
        self.stack = []
        # gesture name
        self.gesture_name = None

        self.fram_count = 10
        self.min_recognize_fram_count = 20
        
        if gesture_name_map:
            with open(gesture_name_map, 'r', newline='') as f:
                map_reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                self.gesture_name = {int(id_float): name_str for id_float, name_str in map_reader}
        
    def clear_queue(self):
        gesture_name,fram_num =  self.recognize()
        self.fram = 20
        self.queue.clear()
        return gesture_name,fram_num

    def pred(self, one_of_multi_hand_world_landmarks):
        sample = extract_and_normlize(one_of_multi_hand_world_landmarks)
        self.queue.append(sample)

        if len(self.queue) == self.max_seq_len:
            t_sample = torch.tensor(self.queue).unsqueeze(0)
            with torch.no_grad():
                t_pred = self.model(t_sample)
                return self._gesture_name(int(torch.argmax(t_pred)))
        else:
            return
    
    def recognize(self):

        length = len(self.queue)
        if self.fram_count >= 10:
            if length >= self.min_recognize_fram_count:
                for i in range(0,length-10,10):
                    # print(i,length)
                    stack = list(itertools.islice(self.queue,i, length))
                    sample = torch.tensor(stack).unsqueeze(0)
                    t_pred = self.model.softmax_pred(sample)
                    self.fram_count = 0
                    if torch.max(t_pred) > 7 :
                        self.queue.clear()
                        return self._gesture_name(int(torch.argmax(t_pred))), length - i
        else:
            self.fram_count += 1

        return 0,0

    def send2(self, one_of_multi_hand_world_landmarks, fingerStraight, fingerUP):
        long_tensor = extract_and_normlize(one_of_multi_hand_world_landmarks)
        long_tensor.extend(fingerStraight)
        long_tensor.extend(fingerUP)
        self.queue.append(long_tensor)
        return self.recognize()
        # self.stack.append(long_tensor)
        
        # gestures = []
        # for i in range(0,len(len_list)):
        #     if length > len_list[i]:
        #         stack = list(itertools.islice(self.queue, 0 , length-1))
        #         sample = torch.tensor(stack).unsqueeze(0)
        #         t_pred = self.model(sample)
        #         if t_pred[0][int(torch.argmax(t_pred))] >0.999:
        #             self.queue.clear()
        #             return self._gesture_name(int(torch.argmax(t_pred))),length
                
        #         for j in range(i,len(len_list)):
        #             stack = list(itertools.islice(self.queue,length - len_list[j], length-1))
        #             sample = torch.tensor(stack).unsqueeze(0)
        #             t_pred = self.model(sample)
        #             if t_pred[0][int(torch.argmax(t_pred))] >0.999 :
        #                 self.queue.clear()
        #                 return self._gesture_name(int(torch.argmax(t_pred))),len_list[j]
        #         break

    def send(self, one_of_multi_hand_world_landmarks, fingerStraight, fingerUP, is_end=None):
        long_tensor = extract_and_normlize(one_of_multi_hand_world_landmarks)
        long_tensor.extend(fingerStraight)
        long_tensor.extend(fingerUP)
        self.stack.append(long_tensor)
        if is_end:
            t_len = len(self.stack)
            t_sample = torch.tensor(self.stack).unsqueeze(0)
            self.stack.clear()
            with torch.no_grad():
                t_pred = self.model.softmax_pred(t_sample)
                # print(t_pred[0][int(torch.argmax(t_pred))])
                print(torch.max(t_pred))
                return self._gesture_name(int(torch.argmax(t_pred))), t_len

    
    
    def _gesture_name(self, id: int):
        if self.gesture_name:
            # offset
            return self.gesture_name[id]
        else:
            return id


if __name__ == '__main__':
    # model legalness check
    test_example = torch.randn(2, 10, 73)
    model = SequenceClassification()
    pred = model(test_example)
    print(pred)
    print(pred.shape)
    print(model.softmax_pred(test_example))
    print(model.softmax_pred(test_example).shape)