"""
Module untuk membuat grafik dan visualisasi data
Menggunakan plotly untuk grafik interaktif
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# ==================== FUNGSI STATISTIK ====================

def calculate_statistics(products_df, transactions_df):
    """
    Fungsi untuk menghitung statistik dasar
    
    Args:
        products_df: DataFrame produk
        transactions_df: DataFrame transaksi
        
    Returns:
        dict: Dictionary berisi statistik
    """
    try:
        stats = {}
        
        # Statistik produk
        stats['total_products'] = len(products_df) if not products_df.empty else 0
        stats['total_stock'] = products_df['stok'].sum() if not products_df.empty else 0
        stats['low_stock_count'] = len(products_df[products_df['stok'] < 10]) if not products_df.empty else 0
        
        # Statistik transaksi hari ini
        if not transactions_df.empty:
            transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
            today = datetime.now().date()
            today_trans = transactions_df[transactions_df['tanggal'] == today]
            
            stats['today_transactions'] = len(today_trans)
            stats['today_revenue'] = today_trans['total_harga'].sum() if not today_trans.empty else 0
            stats['today_profit'] = today_trans['keuntungan'].sum() if not today_trans.empty else 0
        else:
            stats['today_transactions'] = 0
            stats['today_revenue'] = 0
            stats['today_profit'] = 0
        
        # Statistik keseluruhan transaksi
        if not transactions_df.empty:
            stats['total_transactions'] = len(transactions_df)
            stats['total_revenue'] = transactions_df['total_harga'].sum()
            stats['total_profit'] = transactions_df['keuntungan'].sum()
        else:
            stats['total_transactions'] = 0
            stats['total_revenue'] = 0
            stats['total_profit'] = 0
        
        return stats
        
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {
            'total_products': 0,
            'total_stock': 0,
            'low_stock_count': 0,
            'today_transactions': 0,
            'today_revenue': 0,
            'today_profit': 0,
            'total_transactions': 0,
            'total_revenue': 0,
            'total_profit': 0
        }

# ==================== FUNGSI GRAFIK STOK ====================

def create_stock_chart(products_df):
    """
    Fungsi untuk membuat grafik stok produk
    
    Args:
        products_df: DataFrame produk
        
    Returns:
        plotly figure: Grafik stok
    """
    try:
        # Sort berdasarkan stok (descending)
        df_sorted = products_df.sort_values('stok', ascending=False).head(10)
        
        # Buat bar chart
        fig = px.bar(
            df_sorted,
            x='nama_produk',
            y='stok',
            title='Top 10 Produk Berdasarkan Stok',
            labels={'nama_produk': 'Produk', 'stok': 'Jumlah Stok'},
            color='stok',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=400
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating stock chart: {e}")
        return go.Figure()

def create_stock_category_chart(products_df):
    """
    Fungsi untuk membuat grafik stok per kategori
    
    Args:
        products_df: DataFrame produk
        
    Returns:
        plotly figure: Grafik pie stok per kategori
    """
    try:
        # Group by kategori
        category_stock = products_df.groupby('kategori')['stok'].sum().reset_index()
        
        # Buat pie chart
        fig = px.pie(
            category_stock,
            values='stok',
            names='kategori',
            title='Distribusi Stok per Kategori'
        )
        
        fig.update_layout(height=400)
        
        return fig
        
    except Exception as e:
        print(f"Error creating category chart: {e}")
        return go.Figure()

# ==================== FUNGSI GRAFIK PENJUALAN ====================

def create_sales_chart(transactions_df):
    """
    Fungsi untuk membuat grafik penjualan harian
    
    Args:
        transactions_df: DataFrame transaksi
        
    Returns:
        plotly figure: Grafik line penjualan
    """
    try:
        # Convert waktu ke datetime dan extract tanggal
        transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
        
        # Group by tanggal
        daily_sales = transactions_df.groupby('tanggal').agg({
            'total_harga': 'sum',
            'transaksi_id': 'count'
        }).reset_index()
        
        daily_sales.columns = ['tanggal', 'total_penjualan', 'jumlah_transaksi']
        
        # Buat line chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_sales['tanggal'],
            y=daily_sales['total_penjualan'],
            mode='lines+markers',
            name='Total Penjualan (Rp)',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Grafik Penjualan Harian',
            xaxis_title='Tanggal',
            yaxis_title='Total Penjualan (Rp)',
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating sales chart: {e}")
        return go.Figure()

def create_product_sales_chart(transactions_df):
    """
    Fungsi untuk membuat grafik produk terlaris
    
    Args:
        transactions_df: DataFrame transaksi
        
    Returns:
        plotly figure: Grafik bar produk terlaris
    """
    try:
        # Group by produk
        product_sales = transactions_df.groupby('nama_produk').agg({
            'jumlah': 'sum',
            'total_harga': 'sum'
        }).reset_index()
        
        # Sort dan ambil top 10
        product_sales = product_sales.sort_values('jumlah', ascending=False).head(10)
        
        # Buat bar chart
        fig = px.bar(
            product_sales,
            x='nama_produk',
            y='jumlah',
            title='Top 10 Produk Terlaris',
            labels={'nama_produk': 'Produk', 'jumlah': 'Jumlah Terjual'},
            color='jumlah',
            color_continuous_scale='Greens'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=400
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating product sales chart: {e}")
        return go.Figure()

# ==================== FUNGSI GRAFIK KEUNTUNGAN ====================

def create_profit_chart(transactions_df):
    """
    Fungsi untuk membuat grafik keuntungan harian
    
    Args:
        transactions_df: DataFrame transaksi
        
    Returns:
        plotly figure: Grafik keuntungan
    """
    try:
        # Convert waktu ke datetime dan extract tanggal
        transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
        
        # Group by tanggal
        daily_profit = transactions_df.groupby('tanggal').agg({
            'keuntungan': 'sum',
            'total_harga': 'sum'
        }).reset_index()
        
        daily_profit.columns = ['tanggal', 'keuntungan', 'pendapatan']
        
        # Buat bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=daily_profit['tanggal'],
            y=daily_profit['keuntungan'],
            name='Keuntungan',
            marker_color='green'
        ))
        
        fig.update_layout(
            title='Grafik Keuntungan Harian',
            xaxis_title='Tanggal',
            yaxis_title='Keuntungan (Rp)',
            height=400
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating profit chart: {e}")
        return go.Figure()

def create_profit_comparison_chart(transactions_df):
    """
    Fungsi untuk membuat grafik perbandingan pendapatan vs keuntungan
    
    Args:
        transactions_df: DataFrame transaksi
        
    Returns:
        plotly figure: Grafik perbandingan
    """
    try:
        # Convert waktu ke datetime dan extract tanggal
        transactions_df['tanggal'] = pd.to_datetime(transactions_df['waktu']).dt.date
        
        # Group by tanggal
        daily_data = transactions_df.groupby('tanggal').agg({
            'total_harga': 'sum',
            'keuntungan': 'sum'
        }).reset_index()
        
        daily_data.columns = ['tanggal', 'pendapatan', 'keuntungan']
        
        # Buat grouped bar chart
        fig = go.Figure(data=[
            go.Bar(name='Pendapatan', x=daily_data['tanggal'], y=daily_data['pendapatan'], marker_color='lightblue'),
            go.Bar(name='Keuntungan', x=daily_data['tanggal'], y=daily_data['keuntungan'], marker_color='green')
        ])
        
        fig.update_layout(
            title='Perbandingan Pendapatan vs Keuntungan',
            xaxis_title='Tanggal',
            yaxis_title='Rupiah (Rp)',
            barmode='group',
            height=400
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating comparison chart: {e}")
        return go.Figure()

# ==================== FUNGSI GRAFIK KATEGORI ====================

def create_category_revenue_chart(transactions_df, products_df):
    """
    Fungsi untuk membuat grafik pendapatan per kategori
    
    Args:
        transactions_df: DataFrame transaksi
        products_df: DataFrame produk
        
    Returns:
        plotly figure: Grafik pie pendapatan per kategori
    """
    try:
        # Merge transaksi dengan produk untuk mendapatkan kategori
        merged_df = transactions_df.merge(
            products_df[['barcode_id', 'kategori']], 
            on='barcode_id', 
            how='left'
        )
        
        # Group by kategori
        category_revenue = merged_df.groupby('kategori')['total_harga'].sum().reset_index()
        category_revenue.columns = ['kategori', 'pendapatan']
        
        # Buat pie chart
        fig = px.pie(
            category_revenue,
            values='pendapatan',
            names='kategori',
            title='Pendapatan per Kategori'
        )
        
        fig.update_layout(height=400)
        
        return fig
        
    except Exception as e:
        print(f"Error creating category revenue chart: {e}")
        return go.Figure()