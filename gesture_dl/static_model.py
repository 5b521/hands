import torch
from torch import nn

def generate_model(num_classes):
    model = nn.Sequential(
                nn.Dropout(0.2),
                nn.Linear(21*2, 128),
                nn.ReLU(),
                nn.Dropout(0.4),
                nn.Linear(128, 32),
                nn.ReLU(),
                nn.Linear(32, num_classes),
                nn.Softmax(dim=1)
                )
    return model

class StaticClassificationPred:
    def __init__(self, model_path, num_classes) -> None:
        self.model = generate_model(num_classes)
        self.model.load_state_dict(torch.load(model_path))

    def pred(self, one_of_multi_hand_world_landmarks):
        sample = self.extract_and_normlize(one_of_multi_hand_world_landmarks)
        with torch.no_grad():
            pred = self.model(torch.tensor(sample).unsqueeze(0))
            return torch.argmax(pred)

    @staticmethod
    def extract_and_normlize(hand_world_landmarks):
        # results.multi_hand_world_landmarks[0] / or [1]
        # 以手的几何中心为原点建立三维坐标系
        l2 = []
        for lm in hand_world_landmarks.landmark:
            l2.extend([lm.x, lm.y])
        max_value = max(list(map(abs, l2)))
        l3 = list(map(lambda n: n/max_value, l2))
        return l3
        