from typing import List
from torch.utils.data import Dataset, DataLoader

import torch
import csv

def zeropad_collate_fn(batch: List[torch.Tensor]):
    max_len = max([len(tx) for tx, _ in batch])
    
    new_tx_batch = []
    for tx, _ in batch:
        missing = list(tx.shape)
        missing[0] = max_len - tx.shape[0]
        
        if missing[0] > 0:
            padding_tensor = torch.zeros(missing, dtype=tx.dtype, device=tx.device)
            tx = torch.cat([tx, padding_tensor], dim=0)
        
        new_tx_batch.append(tx)
    return torch.stack(new_tx_batch, dim=0), torch.stack([ty for _, ty in batch])


class IPNHandDataset(Dataset):
    def __init__(self, csv_path):
        super().__init__()
        self.X = []
        self.y = []
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.DictReader(f, ['label', 'frames', 'seq_len'], restkey='data', quoting=csv.QUOTE_NONNUMERIC)
            for row in csv_reader:
                label = int(row['label'])
                seq_len = int(row['seq_len'])
                if seq_len != 0:
                    self.X.append(torch.tensor(row['data'], dtype=torch.float32).unflatten(0, (seq_len, -1)))
                    self.y.append(torch.tensor(label, dtype=torch.long))

    def __len__(self):
        return len(self.X)

    def __getitem__(self, index):
        return self.X[index], self.y[index]

class IPNHandStaticDataset(Dataset):
    def __init__(self, csv_path):
        super().__init__()
        self.X = []
        self.y = []
        with open(csv_path, 'r', newline='') as f:
            csv_reader = csv.DictReader(f, ['label'], restkey='data', quoting=csv.QUOTE_NONNUMERIC)
            for row in csv_reader:
                label = int(row['label'])
                self.X.append(torch.tensor(row['data'], dtype=torch.float32))
                self.y.append(torch.tensor(label, dtype=torch.long))
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, index):
        return self.X[index], self.y[index]
    
if __name__ == '__main__':
    dataset = IPNHandDataset('./data/ipn_hand.0.csv')
    train_data_loader = DataLoader(dataset, batch_size=32, shuffle=True, collate_fn=zeropad_collate_fn)
    for batch in train_data_loader:
        # debug to see rightness
        X, y = batch
        while True:
            pass