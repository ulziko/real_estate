import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re
from datetime import datetime

class RentalDataAnalyzer:
    def __init__(self, data_file=None):
        self.df = None
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        """Load data from CSV or JSON file"""
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.df = pd.DataFrame(data)
            print(f"Loaded {len(self.df)} listings from {file_path}")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def clean_price_data(self, df):
        """Clean and validate price data"""
        # Remove rows with no price
        df = df[df['price_value'].notna()]
        
        # Convert to numeric
        df['price_value'] = pd.to_numeric(df['price_value'], errors='coerce')
        
        # Remove invalid prices (0 or negative)
        df = df[df['price_value'] > 0]
        
        # Identify and handle outliers using IQR method
        Q1 = df['price_value'].quantile(0.25)
        Q3 = df['price_value'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define reasonable bounds for rental prices in Mongolia
        lower_bound = max(50000, Q1 - 1.5 * IQR)  # At least 50,000 MNT
        upper_bound = min(50000000, Q3 + 1.5 * IQR)  # At most 50M MNT
        
        # Log outliers before removing
        outliers = df[(df['price_value'] < lower_bound) | (df['price_value'] > upper_bound)]
        if len(outliers) > 0:
            print(f"\nRemoving {len(outliers)} price outliers:")
            for _, row in outliers.head(10).iterrows():
                print(f"  {row['title'][:50]}... - {row['price_value']:,.0f} ₮")
        
        # Filter out outliers
        df = df[(df['price_value'] >= lower_bound) & (df['price_value'] <= upper_bound)]
        
        return df
    
    def clean_area_data(self, df):
        """Clean area data"""
        # Convert to numeric
        df['area_sqm'] = pd.to_numeric(df['area_sqm'], errors='coerce')
        
        # Remove unrealistic areas (less than 10 or more than 1000 sqm)
        df = df[(df['area_sqm'].isna()) | ((df['area_sqm'] >= 10) & (df['area_sqm'] <= 1000))]
        
        return df
    
    def enhance_location_data(self, df):
        """Clean and enhance location data"""
        # Clean district names
        df['district_clean'] = df['district'].str.replace('УБ — ', '').str.strip()
        
        # Map common district variations
        district_mapping = {
            'Баянгол': 'Баянгол',
            'Баянзүрх': 'Баянзүрх', 
            'Сонгинохайрхан': 'Сонгинохайрхан',
            'Сүхбаатар': 'Сүхбаатар',
            'Хан-Уул': 'Хан-Уул',
            'Чингэлтэй': 'Чингэлтэй'
        }
        
        df['district_clean'] = df['district_clean'].map(district_mapping).fillna(df['district_clean'])
        
        return df
    
    def clean_and_prepare_data(self):
        """Main data cleaning function"""
        if self.df is None:
            print("No data loaded")
            return None
        
        print("=== ӨГӨГДӨЛ ЦЭВЭРЛЭХ ===")
        print(f"Анхны өгөгдөл: {len(self.df)} зар")
        
        # Make a copy for cleaning
        df_clean = self.df.copy()
        
        # Clean price data
        df_clean = self.clean_price_data(df_clean)
        print(f"Үнийн өгөгдөл цэвэрлэсний дараа: {len(df_clean)} зар")
        
        # Clean area data
        df_clean = self.clean_area_data(df_clean)
        print(f"Талбайн өгөгдөл цэвэрлэсний дараа: {len(df_clean)} зар")
        
        # Enhance location data
        df_clean = self.enhance_location_data(df_clean)
        
        # Calculate price per square meter
        df_clean['price_per_sqm'] = df_clean['price_value'] / df_clean['area_sqm']
        
        # Clean room data
        df_clean['rooms'] = pd.to_numeric(df_clean['rooms'], errors='coerce')
        df_clean = df_clean[(df_clean['rooms'].isna()) | ((df_clean['rooms'] >= 1) & (df_clean['rooms'] <= 10))]
        
        self.df_clean = df_clean
        return df_clean
    
    def comprehensive_analysis(self):
        """Perform comprehensive market analysis"""
        if not hasattr(self, 'df_clean') or self.df_clean is None:
            print("Please run clean_and_prepare_data() first")
            return
        
        df = self.df_clean
        
        print("\n" + "="*50)
        print("ТҮРЭЭСИЙН ЗАХ ЗЭЭЛИЙН ДЭЛГЭРЭНГҮЙ АНАЛИЗ")
        print("="*50)
        
        print(f"\n📊 ЕРӨНХИЙ МЭДЭЭЛЭЛ:")
        print(f"   Нийт зар: {len(self.df)}")
        print(f"   Цэвэрлэсэн зар: {len(df)}")
        print(f"   Үнэтэй зар: {df['price_value'].notna().sum()}")
        print(f"   Талбайтай зар: {df['area_sqm'].notna().sum()}")
        print(f"   Өрөөний тоотой зар: {df['rooms'].notna().sum()}")
        
        # Price analysis
        print(f"\n💰 ҮНИЙН АНАЛИЗ:")
        price_stats = df['price_value'].describe()
        print(f"   Дундаж: {price_stats['mean']:,.0f} ₮")
        print(f"   Медиан: {price_stats['50%']:,.0f} ₮")
        print(f"   Хамгийн бага: {price_stats['min']:,.0f} ₮")
        print(f"   Хамгийн өндөр: {price_stats['max']:,.0f} ₮")
        print(f"   Стандарт хазайлт: {price_stats['std']:,.0f} ₮")
        
        # Price ranges
        print(f"\n   Үнийн хүрээ:")
        price_ranges = [
            (0, 500000, "500мянга хүртэл"),
            (500000, 1000000, "500м-1сая"),
            (1000000, 2000000, "1-2сая"),
            (2000000, 5000000, "2-5сая"),
            (5000000, float('inf'), "5сая+")
        ]
        
        for min_p, max_p, label in price_ranges:
            count = len(df[(df['price_value'] > min_p) & (df['price_value'] <= max_p)])
            pct = (count / len(df)) * 100
            print(f"     {label}: {count} зар ({pct:.1f}%)")
        
        # Area analysis
        if df['area_sqm'].notna().sum() > 0:
            print(f"\n🏠 ТАЛБАЙН АНАЛИЗ:")
            area_stats = df['area_sqm'].describe()
            print(f"   Дундаж талбай: {area_stats['mean']:.1f} м²")
            print(f"   Медиан талбай: {area_stats['50%']:.1f} м²")
            print(f"   Хамгийн бага: {area_stats['min']:.1f} м²")
            print(f"   Хамгийн том: {area_stats['max']:.1f} м²")
            
            # Price per square meter
            if df['price_per_sqm'].notna().sum() > 0:
                ppsm_stats = df['price_per_sqm'].describe()
                print(f"\n   Нэг м²-ийн үнэ:")
                print(f"     Дундаж: {ppsm_stats['mean']:,.0f} ₮/м²")
                print(f"     Медиан: {ppsm_stats['50%']:,.0f} ₮/м²")
        
        # Location analysis
        print(f"\n🗺️  БАЙРШЛЫН АНАЛИЗ:")
        if 'district_clean' in df.columns:
            district_stats = df.groupby('district_clean').agg({
                'price_value': ['count', 'mean', 'median'],
                'area_sqm': 'mean',
                'price_per_sqm': 'mean'
            }).round(0)
            
            district_stats.columns = ['Тоо', 'Дундаж үнэ', 'Медиан үнэ', 'Дундаж талбай', 'Үнэ/м²']
            district_stats = district_stats.sort_values('Тоо', ascending=False)
            
            print("\n   Дүүрэг бүрээр:")
            for district, row in district_stats.iterrows():
                print(f"     {district}: {int(row['Тоо'])} зар, {int(row['Дундаж үнэ']):,} ₮")
        
        # Room analysis
        if df['rooms'].notna().sum() > 0:
            print(f"\n🏢 ӨРӨӨНИЙ АНАЛИЗ:")
            room_stats = df.groupby('rooms').agg({
                'price_value': ['count', 'mean', 'median'],
                'area_sqm': 'mean'
            }).round(0)
            
            room_stats.columns = ['Тоо', 'Дундаж үнэ', 'Медиан үнэ', 'Дундаж талбай']
            
            print("\n   Өрөөний тоогоор:")
            for rooms, row in room_stats.iterrows():
                print(f"     {int(rooms)} өрөө: {int(row['Тоо'])} зар, {int(row['Дундаж үнэ']):,} ₮")
        
        return df
    
    def create_professional_visualizations(self):
        """Create professional visualizations for the analysis"""
        if not hasattr(self, 'df_clean') or self.df_clean is None:
            print("Please run clean_and_prepare_data() first")
            return
        
        df = self.df_clean
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Price distribution
        ax1 = plt.subplot(3, 3, 1)
        plt.hist(df['price_value'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Түрээсийн үнийн тархалт', fontsize=14, fontweight='bold')
        plt.xlabel('Үнэ (₮)')
        plt.ylabel('Давтамж')
        plt.ticklabel_format(style='plain', axis='x')
        
        # 2. Price by district
        ax2 = plt.subplot(3, 3, 2)
        if 'district_clean' in df.columns:
            district_data = df.groupby('district_clean')['price_value'].median().sort_values(ascending=True)
            district_data.plot(kind='barh', ax=ax2, color='lightcoral')
            plt.title('Дүүрэг бүрийн медиан үнэ', fontsize=14, fontweight='bold')
            plt.xlabel('Үнэ (₮)')
        
        # 3. Area distribution
        ax3 = plt.subplot(3, 3, 3)
        if df['area_sqm'].notna().sum() > 0:
            plt.hist(df['area_sqm'], bins=25, alpha=0.7, color='lightgreen', edgecolor='black')
            plt.title('Талбайн тархалт', fontsize=14, fontweight='bold')
            plt.xlabel('Талбай (м²)')
            plt.ylabel('Давтамж')
        
        # 4. Price vs Area scatter
        ax4 = plt.subplot(3, 3, 4)
        if df['area_sqm'].notna().sum() > 0:
            plt.scatter(df['area_sqm'], df['price_value'], alpha=0.6, color='purple')
            plt.title('Талбай ба үнийн хамаарал', fontsize=14, fontweight='bold')
            plt.xlabel('Талбай (м²)')
            plt.ylabel('Үнэ (₮)')
        
        # 5. Rooms distribution
        ax5 = plt.subplot(3, 3, 5)
        if df['rooms'].notna().sum() > 0:
            room_counts = df['rooms'].value_counts().sort_index()
            room_counts.plot(kind='bar', ax=ax5, color='orange', alpha=0.7)
            plt.title('Өрөөний тооны тархалт', fontsize=14, fontweight='bold')
            plt.xlabel('Өрөөний тоо')
            plt.ylabel('Зарын тоо')
            plt.xticks(rotation=0)
        
        # 6. Price per sqm by district
        ax6 = plt.subplot(3, 3, 6)
        if 'district_clean' in df.columns and df['price_per_sqm'].notna().sum() > 0:
            ppsm_by_district = df.groupby('district_clean')['price_per_sqm'].median().sort_values()
            ppsm_by_district.plot(kind='barh', ax=ax6, color='gold')
            plt.title('Дүүрэг бүрийн м²-ийн үнэ', fontsize=14, fontweight='bold')
            plt.xlabel('Үнэ (₮/м²)')
        
        # 7. Price by rooms
        ax7 = plt.subplot(3, 3, 7)
        if df['rooms'].notna().sum() > 0:
            df_rooms = df[df['rooms'].notna()]
            sns.boxplot(data=df_rooms, x='rooms', y='price_value', ax=ax7)
            plt.title('Өрөөний тоогоор ангилсан үнэ', fontsize=14, fontweight='bold')
            plt.xlabel('Өрөөний тоо')
            plt.ylabel('Үнэ (₮)')
        
        # 8. Monthly trend (if date available)
        ax8 = plt.subplot(3, 3, 8)
        plt.text(0.5, 0.5, 'Зарын статистик\n\nНийт: {} зар\nҮнэтэй: {} зар\nТалбайтай: {} зар'.format(
            len(self.df), 
            df['price_value'].notna().sum(),
            df['area_sqm'].notna().sum()
        ), horizontalalignment='center', verticalalignment='center', 
        transform=ax8.transAxes, fontsize=12,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax8.set_xticks([])
        ax8.set_yticks([])
        ax8.set_title('Өгөгдлийн хураангуй', fontsize=14, fontweight='bold')
        
        # 9. Price range pie chart
        ax9 = plt.subplot(3, 3, 9)
        price_ranges = [
            (0, 1000000, "<1M"),
            (1000000, 2000000, "1-2M"),
            (2000000, 5000000, "2-5M"),
            (5000000, float('inf'), "5M+")
        ]
        
        range_counts = []
        range_labels = []
        for min_p, max_p, label in price_ranges:
            count = len(df[(df['price_value'] > min_p) & (df['price_value'] <= max_p)])
            if count > 0:
                range_counts.append(count)
                range_labels.append(f"{label}\n({count} зар)")
        
        if range_counts:
            plt.pie(range_counts, labels=range_labels, autopct='%1.1f%%', startangle=90)
            plt.title('Үнийн хүрээний тархалт', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('rental_market_analysis_detailed.png', dpi=300, bbox_inches='tight')
        print("\n📊 График rental_market_analysis_detailed.png файлд хадгалагдлаа")
        
        # Show plot if in interactive environment
        try:
            plt.show()
        except:
            print("График харуулах боломжгүй (non-interactive environment)")
    
    def export_clean_data(self, filename='cleaned_rental_data.csv'):
        """Export cleaned data"""
        if hasattr(self, 'df_clean') and self.df_clean is not None:
            self.df_clean.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n💾 Цэвэрлэсэн өгөгдөл {filename} файлд хадгалагдлаа")
            return filename
        else:
            print("Цэвэрлэх өгөгдөл алга")
            return None

# Usage function
def analyze_rental_data(data_file='rental_data.csv'):
    """Main function to analyze rental data"""
    print("🏠 ТҮРЭЭСИЙН ЗАХ ЗЭЭЛИЙН АНАЛИЗ ЭХЭЛЛЭЭ")
    print("="*50)
    
    # Initialize analyzer
    analyzer = RentalDataAnalyzer(data_file)
    
    if analyzer.df is None:
        print("Өгөгдөл ачаалж чадсангүй")
        return None
    
    # Clean data
    df_clean = analyzer.clean_and_prepare_data()
    
    if df_clean is None or len(df_clean) == 0:
        print("Цэвэрлэх өгөгдөл алга")
        return None
    
    # Perform analysis
    analyzer.comprehensive_analysis()
    
    # Create visualizations
    analyzer.create_professional_visualizations()
    
    # Export clean data
    analyzer.export_clean_data()
    
    return analyzer

# Run the analysis
if __name__ == "__main__":
    analyzer = analyze_rental_data('rental_data.csv')