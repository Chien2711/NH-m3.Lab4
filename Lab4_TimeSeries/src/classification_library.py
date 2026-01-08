import pandas as pd
import numpy as np
import zipfile
import os

class AirQualityLoader:
    """
    Lớp dùng để tải và xử lý sơ bộ dữ liệu chất lượng không khí Bắc Kinh.
    Theo đúng yêu cầu Lab 4: OOP style.
    """
    def __init__(self, zip_path):
        self.zip_path = zip_path
        self.raw_data = None
        self.clean_data = None

    def load_raw_data(self):
        """Đọc dữ liệu từ file zip và gộp 12 trạm thành 1 DataFrame."""
        print(f"Dang doc du lieu tu: {self.zip_path}")
        
        if not os.path.exists(self.zip_path):
            raise FileNotFoundError(f"Khong tim thay file: {self.zip_path}")

        df_list = []
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            # Liet ke cac file csv trong zip
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            print(f"Tim thay {len(csv_files)} file CSV trong file zip.")
            
            for csv_file in csv_files:
                with z.open(csv_file) as f:
                    df = pd.read_csv(f)
                    df_list.append(df)
        
        # Gop tat ca cac tram lai
        self.raw_data = pd.concat(df_list, axis=0, ignore_index=True)
        print(f"Da gop xong. Kich thuoc du lieu thô: {self.raw_data.shape}")
        return self.raw_data

    def preprocess(self):
        """Làm sạch dữ liệu và tạo cột datetime."""
        if self.raw_data is None:
            self.load_raw_data()
            
        df = self.raw_data.copy()
        
        # 1. Tao cot datetime tu year, month, day, hour
        print("Dang xu ly thoi gian...")
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        
        # 2. Xoa cac cot thoi gian le
        df.drop(columns=['year', 'month', 'day', 'hour', 'No'], inplace=True, errors='ignore')
        
        # 3. Sap xep theo Tram va Thoi gian
        df.sort_values(by=['station', 'datetime'], inplace=True)
        
        # 4. Xu ly thieu du lieu (Missing Values) - Dien bang phuong phap noi suy (interpolate) hoac ffill
        # O day dung ffill (dien gia tri truoc do) cho don gian theo nguyen tac chuoi thoi gian
        cols_to_fill = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
        for col in cols_to_fill:
            if col in df.columns:
                df[col] = df.groupby('station')[col].ffill().bfill()
                
        self.clean_data = df
        print(f"Xu ly xong. Kich thuoc du lieu sach: {self.clean_data.shape}")
        return self.clean_data