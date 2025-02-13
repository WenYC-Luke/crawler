import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager

class StockAnalysis:
    
    def __init__(self):
        self.font = font_manager.FontProperties(fname=r"C:\Windows\Fonts\msjhbd.ttc")
        
        self.useData = None  # 用於儲存數據
        
        # 柱狀圖
        self.totalBuy = 0  # 總買入
        self.totalSell = 0  # 總賣出
        self.onlyBuyList = [[], [], []]  # 純買進列表
        self.onlySellList = [[], [], []]  # 純賣出列表
        self.forBuySellList = [[] for _ in range(6)]  # 買進賣出列表
        
        # 散佈圖
        self.s_price_buy = {}
        self.s_person = {}
        self.m_price_buy = {}
        self.m_person = {}
        self.l_price_buy = {}
        self.l_person = {}
        
        
    def data_prepare(self, file):
        data = pd.read_csv(f"./stockdata/{file}.csv",encoding='Big5', skiprows=2)
        data1 = data[['券商', '價格', '買進股數', '賣出股數']]
        data2 = data[['券商.1', '價格.1','買進股數.1', '賣出股數.1']]
        data2.columns = ['券商', '價格', '買進股數', '賣出股數']
        self.useData = pd.concat([data1, data2]).dropna()
        
    
    # start--柱狀圖------------------------------------------------------------------------------------------
    def bar_chart_data(self):

        # 今日買賣
        buyAndSells = self.useData[["買進股數", "賣出股數"]].astype(float)
        
        self._onlyBuy(buyAndSells)
        self._onlySell(buyAndSells)
        self._onlyBuyAndSell(buyAndSells)
        
    def _onlyBuy(self, buyAndSells):
        # 純買進
        onlyBuy = buyAndSells[(buyAndSells["買進股數"] != 0) & (buyAndSells["賣出股數"] == 0)]["買進股數"]

        for buy in onlyBuy:
            if buy <= 1000:
                self.onlyBuyList[0].append(buy)
            elif buy <= 5000:
                self.onlyBuyList[1].append(buy)
            else:
                self.onlyBuyList[2].append(buy)

        
    def _onlySell(self, buyAndSells):
        # 純賣出
        onlySell = buyAndSells[(buyAndSells["賣出股數"] != 0) & (buyAndSells["買進股數"] == 0)]["賣出股數"]

        for sell in onlySell:
            if sell <= 1000:
                self.onlySellList[0].append(sell)
            elif sell <= 5000:
                self.onlySellList[1].append(sell)
            else:
                self.onlySellList[2].append(sell)
                
     
    def _onlyBuyAndSell(self, buyAndSells):           
        # 買進賣出        
        buyAndSells = buyAndSells[(buyAndSells["買進股數"] != 0) & (buyAndSells["賣出股數"] != 0)]

        for idx, forBuySell in buyAndSells.iterrows():
            forBuy = forBuySell["買進股數"]
            forSell = forBuySell["賣出股數"]

            if (forBuy + forSell)/2 <= 1000:
               self.forBuySellList[0].append(forBuy)  # 散戶(買)
               self.forBuySellList[1].append(forSell) # 散戶(賣)
                
            elif (forBuy + forSell)/2 <= 5000:
               self.forBuySellList[2].append(forBuy)  # 中戶(買)
               self.forBuySellList[3].append(forSell) # 中戶(賣)
            
            else:
               self.forBuySellList[4].append(forBuy)  # 大戶(買) 
               self.forBuySellList[5].append(forSell) # 大戶(賣)       
                
               
    
    def bar_chart_frame(self, index, x_data, y_data, title):
        plt.subplot(3, 1, index)
        barWidth = 0.5

        plt.bar(x_data, y_data, width=barWidth, color=["#F27405", "#731702", "#02735E", "#014040"],label=y_data, zorder=3)

        plt.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.8, zorder=0)
        plt.setp(plt.gca().get_xticklabels(), visible=index == 3, font=self.font, fontsize=18)  # 只在最後一個顯示 x 軸標籤
        
        plt.title(title, font=self.font, fontsize=24, pad=15)
        plt.yticks(fontsize=16)
        plt.ylabel("交易張數", font=self.font, fontsize=20, labelpad=15)

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=True, edgecolor='black', fontsize=16)    
    
   
    def bar_chart_draw(self):
        # 1. 準備數據 
        x_data = ["純買", "純賣", "有交易(買)", "有交易(賣)"]
        y_datas = [
            [sum(self.onlyBuyList[0])/1000, sum(self.onlySellList[0])/1000, sum(self.forBuySellList[0])/1000, sum(self.forBuySellList[1])/1000],
            [sum(self.onlyBuyList[1])/1000, sum(self.onlySellList[1])/1000, sum(self.forBuySellList[2])/1000, sum(self.forBuySellList[3])/1000], 
            [sum(self.onlyBuyList[2])/1000, sum(self.onlySellList[2])/1000, sum(self.forBuySellList[4])/1000, sum(self.forBuySellList[5])/1000]
        ]

        # 4. 設置外觀參數
        plt.figure(figsize=(10, 16), facecolor='lightgrey')

        # 2. 繪製圖片
        
        titles = ["散戶", "中戶", "大戶"]
        
        for idx, (y_data, title) in enumerate(zip(y_datas, titles), start=1):  # 產生(1, (y_data1, 'Title1')), (2, (y_data2, 'Title2')), (3, (y_data3, 'Title3'))
            self.bar_chart_frame(idx, x_data, y_data, title)
        
        plt.tight_layout()
        plt.show()
        
    # end--柱狀圖------------------------------------------------------------------------------------------
        
    # start--散佈圖----------------------------------------------------------------------------------------
    
    # 數據分類
    def classtify_forScaHeat(self, avg, price_Data, buy_Data):
        # 根據股數區分散戶/中戶/大戶
        if  avg <= 1000:
            self.forScaHeatData(self.s_price_buy, self.s_person, price_Data, buy_Data) # 散戶
        elif avg <= 5000:
            self.forScaHeatData(self.m_price_buy, self.m_person, price_Data, buy_Data) # 中戶
        else:
            self.forScaHeatData(self.l_price_buy, self.l_person, price_Data, buy_Data) # 大戶

      
    def forScaHeatData(self, price_buy, person, price_Data, buy_Data):
        # 分類字典
        if price_Data not in price_buy:
            price_buy[price_Data] = buy_Data
            person[price_Data] = 1
        else:
            price_buy[price_Data] += buy_Data
            person[price_Data] += 1
 
    
    def forScatter_drawData(self): 
        # 散戶 散佈圖數據(畫圖)
        self.scatterPriceBuyS = pd.DataFrame({"價格": list(self.s_price_buy.keys()), "股數": list(self.s_price_buy.values())})
        self.scatterPricePersonS = pd.DataFrame({"價格": list(self.s_person.keys()), "人數": list(self.s_person.values())}) 
    
        # 中戶 散佈圖數據(畫圖)
        self.scatterPriceBuyM = pd.DataFrame({"價格": list(self.m_price_buy.keys()), "股數": list(self.m_price_buy.values())})
        self.scatterPricePersonM = pd.DataFrame({"價格": list(self.m_person.keys()), "人數": list(self.m_person.values())}) 
    
        # 大戶 散佈圖數據(畫圖)
        self.scatterPriceBuyL = pd.DataFrame({"價格": list(self.l_price_buy.keys()), "股數": list(self.l_price_buy.values())})
        self.scatterPricePersonL = pd.DataFrame({"價格": list(self.l_person.keys()), "人數": list(self.l_person.values())}) 
    
    def scatter_plot_data(self):
        # 原始數據分離資料
        priceBuySellData = self.useData[["價格","買進股數","賣出股數"]].astype(float)

        for idx, eachData in  priceBuySellData.iterrows():
            price_Data = eachData["價格"]
            buy_Data = eachData["買進股數"]
            sell_Data = eachData["賣出股數"]
            
            avg = (buy_Data + sell_Data) /2
            
            self.classtify_forScaHeat(avg, price_Data, buy_Data)
            

    def Scatter_plot_draw(self):
        plt.figure(figsize=(8,8),facecolor='lightgrey')
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.8, zorder=0 )
        

        sns.scatterplot(x="人數", y="價格", data=self.scatterPricePersonS, s=self.scatterPricePersonS["人數"], color="red", alpha=0.5, label="散戶")
        sns.scatterplot(x="人數", y="價格", data=self.scatterPricePersonM, s=self.scatterPricePersonM["人數"], color="green", alpha=0.5, label="中戶")
        sns.scatterplot(x="人數", y="價格", data=self.scatterPricePersonL, s=self.scatterPricePersonL["人數"], color="blue", alpha=0.5, label="大戶")

        plt.title("交易熱點圖", font=self.font, fontsize=28, pad=15)
        plt.xticks(fontsize=14)
        plt.xlabel("人數", font=self.font, fontsize=18, labelpad=15)
        plt.yticks(fontsize=14)
        plt.ylabel("價格", font=self.font, fontsize=18, labelpad=15)

        # 特別設置圖替修改方式(受sns干擾)
        legend = plt.legend(prop=self.font, loc='center left', bbox_to_anchor=(1, 0.5), frameon=True)
        plt.setp(legend.get_texts(), fontsize=18) 

        # 特別設置圖例圓點的大小
        for handle in legend.legendHandles:
            handle._sizes = [200]

        plt.show()
        
    # end--散佈圖------------------------------------------------------------------------------------------      
   
    # start--熱力圖----------------------------------------------------------------------------------------
    def Heap_map_frame(self, data, title, index):     
        
        # 子圖
        plt.subplot(1, 3, index)
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.8, zorder=0 )
        
        heatmap_data = data.pivot(index="價格", columns="股數", values="股數")
        sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt='.0f', linewidths=0.5,annot_kws={"fontsize": 20})
        
        plt.title(title, font=self.font, fontsize=28, pad=20)
        plt.xticks(rotation=0,fontsize=18)
        plt.xlabel("股數", font=self.font, fontsize=24, labelpad=15)

        # y軸顯示翻轉
        plt.gca().invert_yaxis()
        plt.ylabel("價格", font=self.font, fontsize=24, labelpad=15)
        plt.yticks(fontsize=18) 
        
    # 熱力圖    
    def Heat_map_draw(self):
        
        plt.figure(figsize=(36,8), facecolor="lightgray")
        
        self.Heap_map_frame(self.scatterPriceBuyS, "散戶", 1)
        self.Heap_map_frame(self.scatterPriceBuyM, "中戶", 2)
        self.Heap_map_frame(self.scatterPriceBuyL, "大戶", 3)

        plt.tight_layout()
        plt.show()
        
        # end--熱力圖------------------------------------------------------------------------------------------
    
    
    def getData(self, file):
        
        # 柱狀圖資料
        stock_purchase = {
            "散戶" : {"純買人數": len(self.onlyBuyList[0]), "純買張數": sum(self.onlyBuyList[0])/1000,
                      "純賣人數": len(self.onlySellList[0]), "純賣張數": sum(self.onlySellList[0])/1000,
                      "有交易人數": len(self.forBuySellList[0]), "有交易張數(買)": sum(self.forBuySellList[0])/1000, "有交易張數(賣)": sum(self.forBuySellList[1])/1000
                    },
            
            "中戶" : {"純買人數": len(self.onlyBuyList[1]), "純買張數": sum(self.onlyBuyList[1])/1000,
                      "純賣人數": len(self.onlySellList[1]), "純賣張數": sum(self.onlySellList[1])/1000,
                      "有交易人數": len(self.forBuySellList[2]), "有交易張數(買)": sum(self.forBuySellList[2])/1000, "有交易張數(賣)": sum(self.forBuySellList[3])/1000
                    },
            
            "大戶" : {"純買人數": len(self.onlyBuyList[2]), "純買張數": sum(self.onlyBuyList[2])/1000,
                     "純賣人數": len(self.onlySellList[2]), "純賣張數": sum(self.onlySellList[2])/1000,
                     "有交易人數": len(self.forBuySellList[4]), "有交易張數(買)": sum(self.forBuySellList[4])/1000, "有交易張數(賣)": sum(self.forBuySellList[5])/1000
                    }
            }
        
        
        # 散佈圖/熱力圖資料
        mergeData = []
        for price in self.s_price_buy:
            if (price in self.s_person and 
                price in self.m_price_buy and price in self.m_person and 
                price in self.l_price_buy and price in self.l_person):                
                
                mergeData.append({
                    "價格": price,
                    "散戶購買張數": self.s_price_buy[price],
                    "散戶購買人數": self.s_person[price],
                    "中戶購買張數": self.m_price_buy[price],
                    "中戶購買人數": self.m_person[price],                    
                    "大戶購買張數": self.l_price_buy[price],
                    "大戶購買人數": self.l_person[price]
                    })
                    
                    
        # 轉換成表格
        df_stock_purchase = pd.DataFrame.from_dict(stock_purchase, orient="index")
        df_mergeData = pd.DataFrame(mergeData)

        # 輸出到excel
        with pd.ExcelWriter(f"{file}_output.xlsx") as df_data:
            df_stock_purchase.to_excel(df_data, sheet_name='Stock Purchase')
            df_mergeData.to_excel(df_data, sheet_name='Merge Data', index=False)
        
# 主程式
def main():
    stock_analysis = StockAnalysis()
    
    #目前資料夾為./stockdata/XXX.csv
    file = input("請輸入(代號_日期) 例如: 3231_20241018:  ")
    stock_analysis.data_prepare(file)
    
    
    stock_analysis.bar_chart_data()  # 準備柱狀圖數據
    stock_analysis.scatter_plot_data()  # 準備散佈圖數據
    stock_analysis.forScatter_drawData()  # 準備熱力圖數據
    stock_analysis.getData(file) # 準備數據    

    
    # 繪製圖表
    chart_types = input("請選擇要繪製的圖表類型 (1: 柱狀圖, 2: 散佈圖, 3: 熱力圖, all: 全部 ) 代號用','分隔: ")
    chart_types = chart_types.split(",")  # 以逗號分隔輸入的選擇

    if "1" in chart_types:
        stock_analysis.bar_chart_draw()  # 繪製柱狀圖
    if "2" in chart_types:
        stock_analysis.Scatter_plot_draw()  # 繪製散佈圖
    if "3" in chart_types:
        stock_analysis.Heat_map_draw()  # 繪製熱力圖
    
    if "all" in chart_types:
        stock_analysis.bar_chart_draw()
        stock_analysis.Scatter_plot_draw()
        stock_analysis.Heat_map_draw()
    
        
if __name__ == "__main__":
    main()