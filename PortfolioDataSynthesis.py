#Importing pandas for excel-style data manipulation
#import pandas as pd
import os
import sys
import pandas as pd
#This is where I typically get S&P 500 data
#https://www.wsj.com/market-data/quotes/index/SPX/historical-prices

#Default file locations. CSV files used for the purposes of this program
portfolioBalanceFile = 'AmeritradeBalanceData.csv'
comparisonPricingFile = "HistoricalPrices.csv"
depositsFile = "DepositInfo.csv"
#outFile = what filename to save completed dataframe as
outFile = "PortfolioComparisonAnalysis.csv"

#Allow the user to specify alternate files
print('Before choosing files, make sure to clean impurities in data')
specifiedFile = input('Specify a file for Ameritrade balance data. Leave blank for default (AmeritradeBalanceData.csv): ')
if (specifiedFile and os.path.exists(os.path.join(os.getcwd(), specifiedFile))):
    portfolioBalanceFile = specifiedFile
specifiedFile = input('Specify a file for comparison index data. Leave blank for default (HistoricalPrices.csv): ')
if (specifiedFile and os.path.exists(os.path.join(os.getcwd(), specifiedFile))):
    comparisonPriceData = specifiedFile
specifiedFile = input('Specify a file for account deposits data. Leave blank for default (DepositInfo.csv): ')
if (specifiedFile and os.path.exists(os.path.join(os.getcwd(), specifiedFile))):
    depositsData = specifiedFile
specifiedFile = input('Specify a file for final cleaned/synthesized data. Leave blank for default (PortfolioComparisonAnalysis.csv): ')
if (specifiedFile and os.path.exists(os.path.join(os.getcwd(), specifiedFile))):
    outFile = specifiedFile

#Removes all 0s from a date. Used to keep all dates consistent
def cleanDate(dateString):
    partsOfDate = dateString.split("/")
    for i in range(3):
        #Converting each part of the date to int then back to string removes leading zeros
        partsOfDate[i] = str(int(partsOfDate[i]))
    return '/'.join(partsOfDate)

#Removes all commas from a cell/number and turns it into a float
def convertToInt(numberAsString):
    return float(numberAsString.replace(",", ""))

#Rounds numerical cells to 4 decimal places
def roundDecimals(cellValue):
    try:
        return round(cellValue, 4)
    except:
        return cellValue

#Reads in all the csv files and turns them into pandas dataframes
portfolioBalanceData = pd.read_csv(portfolioBalanceFile)
comparisonPriceData = pd.read_csv(comparisonPricingFile)
depositsData = pd.read_csv(depositsFile)

portfolioBalanceData['Date'] = portfolioBalanceData['Date'].apply(cleanDate)

#totalDataFrame starts with the comparison data because it has less dates. Then the brokerage data is added
totalDataFrame = comparisonPriceData

#The imported wsj data has spaces at the start of each heading. Heading labels are not renamed until the end
#This portion would have to change if the user retrieved data from a different source
totalDataFrame = totalDataFrame.drop([" Open", " High", " Low"], axis=1)

#Use cumulative sum to add up all the prior deposit entries
depositsData['Cumulative deposits'] = (depositsData['Deposit']).cumsum()

#Put the portfolio/brokerage data and the deposits data into the totalDataFrame. Set Date as the key/limiting factor to prevent extra dates from the brokerage data
totalDataFrame = totalDataFrame.set_index('Date').join(portfolioBalanceData.set_index('Date'))
totalDataFrame = totalDataFrame.join(depositsData.set_index('Date'))

#Shift deposits and cumulative deposits down by 1 because Ameritrade stores them a day early compared to account value
#EDIT: This should not have been shifted. Only the first 3 deposits had this issue. I just manually adjusted those deposits.
#totalDataFrame['Deposit'] = totalDataFrame['Deposit'].shift(periods=1)
#totalDataFrame['Cumulative deposits'] = totalDataFrame['Cumulative deposits'].shift(periods=1)

#Computes the amount of comparison shares bought based on the closing price and deposit amount
totalDataFrame['Comparison shares bought'] = (totalDataFrame['Deposit'])/totalDataFrame[' Close']
#Use cumulative sum to add up all the prior 'comparison shares bought' entries
totalDataFrame['Cumulative comparison shares'] = (totalDataFrame['Comparison shares bought']).cumsum()

#ffill is shorthand for .fillna(method='ffill') and basically replaces NaN values with the value above them in the chart
totalDataFrame[['Account value', 'Cumulative deposits', 'Cumulative comparison shares']] = totalDataFrame[['Account value', 'Cumulative deposits', 'Cumulative comparison shares']].ffill()

#Replaces any remaining NaN with 0. This accounts for the top row since ffill doesn't work there (nothing above to copy from)
totalDataFrame.fillna(0, inplace=True)

#Convert all account values to numbers without commas
totalDataFrame['Account value'] = totalDataFrame['Account value'].apply(convertToInt)

#Calculate how much the comparison account would have by multiplying comparison shares by the close price.
totalDataFrame['Comparison account value'] = totalDataFrame['Cumulative comparison shares']*totalDataFrame[' Close']

#Calculate the percentage of the comparison that the account is. 100% = equal
totalDataFrame['Account as percentage of comparison'] = totalDataFrame['Account value']/totalDataFrame['Comparison account value']
totalDataFrame['Account as percentage of comparison'][0] = 1

#Take the account percentage and multiply by comparison share price to get hypothetical account share price
totalDataFrame['Hypothetical account share price'] = totalDataFrame['Account as percentage of comparison']*totalDataFrame[' Close']

#Rounds all cells to make the printed data neater
totalDataFrame = totalDataFrame.apply(roundDecimals)

#Renames the Close column to be more descriptive and removes extra space.
#For this program I did it at the end. I am not sure whether that is good or bad practice.
totalDataFrame = totalDataFrame.rename(columns={" Close": "Comparison price"})

totalDataFrame.to_csv(outFile)#index=False)

#print(totalDataFrame.head(50))