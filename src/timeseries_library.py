import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

class ARIMAForecaster:
    """
    Class hỗ trợ phân tích và dự báo chuỗi thời gian bằng ARIMA
    """
    def __init__(self, data):
        # Dữ liệu đầu vào chỉ cần 2 cột: datetime và PM2.5
        self.data = data.set_index('datetime').sort_index()
        # Đảm bảo tần suất là Hourly (H)
        self.data = self.data.asfreq('H')
        self.model_fit = None

    def check_stationarity(self, col='PM2.5'):
        """Kiểm tra tính dừng bằng ADF Test"""
        print(f"--- Kiem tra tinh dung (ADF Test) cho: {col} ---")
        series = self.data[col].dropna()
        result = adfuller(series)
        
        print(f'ADF Statistic: {result[0]}')
        print(f'p-value: {result[1]}')
        
        if result[1] < 0.05:
            print("=> Ket luan: Chuoi la chuoii DUNG (Stationary). Co the chon d=0.")
            return True
        else:
            print("=> Ket luan: Chuoi KHONG dung. Can sai phan (d=1).")
            return False

    def plot_acf_pacf(self, col='PM2.5', lags=40):
        """Vẽ biểu đồ ACF và PACF để chọn p, q"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 5))
        series = self.data[col].dropna()
        
        plot_acf(series, lags=lags, ax=axes[0])
        axes[0].set_title("Autocorrelation (Gợi ý q)")
        
        plot_pacf(series, lags=lags, ax=axes[1])
        axes[1].set_title("Partial Autocorrelation (Gợi ý p)")
        
        plt.show()

    def train_arima(self, order=(1, 0, 1), col='PM2.5'):
        """Huấn luyện mô hình ARIMA với tham số (p,d,q)"""
        print(f"Dang train ARIMA voi order={order}...")
        series = self.data[col].dropna()
        
        # Chia train/test thủ công (lấy 24h cuối để test thử)
        train_size = int(len(series) * 0.95)
        train, test = series[0:train_size], series[train_size:]
        self.test_data = test # Lưu lại để đánh giá
        
        model = ARIMA(train, order=order)
        self.model_fit = model.fit()
        print("Da train xong!")
        print(self.model_fit.summary())
        return self.model_fit

    def forecast_and_evaluate(self):
        """Dự báo trên tập test và đánh giá"""
        if self.model_fit is None:
            print("Vui long train model truoc!")
            return

        # Dự báo cho khoảng thời gian của tập test
        start = len(self.data) - len(self.test_data)
        end = len(self.data) - 1
        
        predictions = self.model_fit.predict(start=start, end=end, type='levels')
        
        # Đánh giá
        rmse = np.sqrt(mean_squared_error(self.test_data, predictions))
        mae = mean_absolute_error(self.test_data, predictions)
        
        print(f"--- KET QUA DANH GIA ARIMA ---")
        print(f"RMSE: {rmse:.2f}")
        print(f"MAE: {mae:.2f}")
        
        return self.test_data, predictions