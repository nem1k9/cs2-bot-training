import torch
import torch.nn as nn
import torch.nn.functional as F

class CausalConv1d(nn.Module):
    def __init__(self, in_ch, out_ch, kernel=3, dilation=1):
        super().__init__()
        self.padding = (kernel - 1) * dilation
        self.conv = nn.Conv1d(in_ch, out_ch, kernel,
                              dilation=dilation, padding=self.padding)
    def forward(self, x):
        return self.conv(x)[:, :, :-self.padding]


class TCNBlock(nn.Module):
    def __init__(self, channels, kernel=3, dilation=1):
        super().__init__()
        self.conv1 = CausalConv1d(channels, channels, kernel, dilation)
        self.conv2 = CausalConv1d(channels, channels, kernel, dilation)
        self.norm1 = nn.LayerNorm(channels)
        self.norm2 = nn.LayerNorm(channels)

    def forward(self, x):
        r = x
        x = F.gelu(self.norm1(self.conv1(x).transpose(1,2)).transpose(1,2))
        x = self.norm2(self.conv2(x).transpose(1,2)).transpose(1,2)
        return F.gelu(x + r)


class CS2BotModel(nn.Module):
    def __init__(self, state_dim=22, hidden=256):
        super().__init__()

        self.tick_encoder = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Linear(128, 128),
        )

        self.tcn = nn.Sequential(
            TCNBlock(128, dilation=1),
            TCNBlock(128, dilation=2),
            TCNBlock(128, dilation=4),
        )

        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=hidden,
            num_layers=2,
            batch_first=True,
            dropout=0.15
        )

        self.fusion = nn.Sequential(
            nn.Linear(128 + hidden, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Linear(256, 128),
            nn.GELU(),
        )

        self.move_head = nn.Sequential(
            nn.Linear(128, 64), nn.GELU(),
            nn.Linear(64, 5),   # W A S D + CROUCH
            nn.Sigmoid()
        )
        self.aim_head = nn.Sequential(
            nn.Linear(128, 64), nn.GELU(),
            nn.Linear(64, 2),   # dyaw, dpitch
            nn.Tanh()
        )
        self.action_head = nn.Sequential(
            nn.Linear(128, 64), nn.GELU(),
            nn.Linear(64, 4),   # shoot, jump, reload, use
            nn.Sigmoid()
        )

    def forward(self, state_seq, lstm_hidden=None):
        B, T, D = state_seq.shape

        ticks = self.tick_encoder(state_seq.reshape(B*T, D))
        ticks = ticks.reshape(B, T, 128)

        tcn_in   = ticks.transpose(1, 2)
        tcn_out  = self.tcn(tcn_in)
        tcn_last = tcn_out[:, :, -1]

        lstm_out, lstm_hidden = self.lstm(ticks, lstm_hidden)
        lstm_last = lstm_out[:, -1, :]

        fused = self.fusion(
            torch.cat([tcn_last, lstm_last], dim=-1)
        )

        return {
            "move":   self.move_head(fused),
            "aim":    self.aim_head(fused),
            "action": self.action_head(fused),
        }, lstm_hidden