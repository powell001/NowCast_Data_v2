library(tidyverse)
library(xts)
library(zoo)
library(svglite)
library(TSstudio)
library(zoo)
library(dlm)
library(forecast)
library(expsmooth)
library(ggplot2)
#library(ggfortify)
library(changepoint)
library(KFAS)
library(httpgd)
library(funtimes)
library(seastests)
library(car)
library(lmtest)

# Time series plots
# https://cran.rstudio.com/web/packages/ggfortify/vignettes/plot_ts.html

figures_dir  <- "output_qt/figures/"
analyse_dir  <- "output_qt/analyses/"
forecast_dir <- "output_qt/forecasts/"

# Model consists of three letters following Hyndman (2008) and here: https://search.r-project.org/CRAN/refmans/forecast/html/ets.html

# First letter is the error type:     A, M or Z
# Second letter is the trend type:    N, A, M, Z
# Third letter is the season type:    N, A, M, Z

# Some of the models have names:
#     ANN is simple exponential smoothing with additive errors.
#     MAM is multiplicative Holt-Winters with multiplicative errors.


##########################

### Horizons
horizon <- 1  # should be 1 in general

# load data
dt1 <- read.csv("output_combined/a0_combinedQuarterly.csv", sep = ",")

# remove files
do.call(file.remove, list(list.files(forecast_dir, full.names = TRUE)))
do.call(file.remove, list(list.files(figures_dir, full.names = TRUE)))

allColumns <- colnames(dt1)

fill_df <- dt1

##########################
# FOR LOOP
##########################

for(colName in allColumns){ 

#dont want to forecast date
if (colName == "X") {next}

#colName <- "gdp_total"

print(colName)

# Key1 connects all the data
Key1 <- paste(Sys.Date(), "_", colName, sep="")

series1 <- ts(dt1[colName], frequency = 4, start=c(1995,1))

# if missing many values, flag it
if (sum(is.na(series1)) > 50) {   ###### This is effectively not a constraint when set so high
  print(paste0("Removing:", colName))
  }

# drop nas, date will remain the same
series1 <- na.omit(series1, cex.main = 6, col.main = "darkgreen")

plot(series1, main = colName)

# check if series contains negative numbers
if (any(as.numeric(series1) < 0)) {
  modelform <- "AAA"
  print("Data contains negative numbers")

} else {

  #########################
  # Which model to use
  #########################

  ###########################
  # Trend or not?
  ###########################

  p_value <- try(notrend_test(series1)$p.value)
  print(p_value)

  if (is.numeric(p_value) == FALSE) {
    print("assume: Has Trend")
    trendtype <- "A"
  } else {
      if (p_value < 0.05) { ############################# CHECK THIS ######################
        print("Has Trend")
        trendtype <- "A"
      } else {
        print("No Trend")
        trendtype <- "N"
        }
  }

  print(trendtype)

  ###########################
  # Additive or multiplictive?
  ###########################

  decompose_series1 <- decompose(series1, "multiplicative")
  decompose_series1_multiplicative <- decompose_series1$random
  muladd_mul <- sqrt(mean(abs(decompose_series1_multiplicative)^2, na.rm=TRUE))

  decompose_series1 <- decompose(series1, "additive")
  decompose_series1_additive <- decompose_series1$random
  muladd_add <- sqrt(mean(abs(decompose_series1_additive)^2, na.rm=TRUE))

  if (muladd_mul < muladd_add) {
    print("Use Multiplicative")
    errortype <- "M"
    } else {
      print("Use Additive")
      errortype <- "A"
  }

  print(errortype)

  ###########################
  # Seasonnal or not
  ###########################

  season_Check <- isSeasonal(series1)

  if (season_Check == TRUE) {
    print("Use Seasonal")
    seasontype <- "A"
    } else {
      print ("Use Non-Seasonal")
      seasontype <- "N"
    }

  print(seasontype)

  modelform <- str_c(c(errortype, trendtype, seasontype), collapse = "")
  } # end if for negative numbers

###############
# above, if negative numbers use simple method
###############

fit <- ets(series1, model=modelform, damped=FALSE)

############
# test period
#############
test_period <- 12

h1 <- test_period
train <- head(series1, round(length(series1) - h1))
test <- tail(series1, h1)

fit <- ets(train, model=modelform, damped=FALSE)
forecasted1 <- forecast(fit, h=h1)

png(filename=paste(figures_dir, Key1, "TrainTestForecast.png", sep = "_"))
print(autoplot(forecasted1, series = "In-sample Forecast", include=h1+16) + autolayer(test, series = "Historical Data") + ggtitle(colName)) + ylab("Historical + Forecast")
dev.off()

####################
# final forecast
####################
fit <- ets(series1, model=modelform, damped=FALSE)
forecast_oneQuarter <- forecast(fit, h = horizon)

png(filename=paste(figures_dir, Key1, "final_forecasts.png", sep = "_"))
print(autoplot(tail(series1, 20)) + autolayer(forecast_oneQuarter) + ggtitle(colName))
dev.off()

################################
# Saving
################################

###
# Raw Data
###

data <- data.frame(
  SeriesName   = colName, 
  DateAnalysis = Sys.Date(), 
  ETSmodel = modelform,
  ObservationDate = as.yearqtr(time(series1)),  ##### Careful here, yearmon is not the same as yearqtr
  RawData = series1
)
data$Key1 <- Key1

###
# TrainTestForecast
###
forecast_tibble <- as.data.frame(forecasted1)
forecast_tibble$Key1 <- Key1 

write.table(forecast_tibble, file = paste(forecast_dir, Key1, "TrainTestForecast.csv", sep="_"), sep =",",row.names = FALSE)

###
# finalForecast
###
forecast_oneQuarter <- forecast(fit, h = horizon)
finalForecast <- as.data.frame(forecast_oneQuarter, row.names = NULL)
finalForecast$Key1 <- Key1
finalForecast <- tibble::rownames_to_column(finalForecast, "Forecast_Period")  

write.table(finalForecast, file = paste(forecast_dir, Key1, "final_forecasts.csv", sep="_"), sep =",",row.names = FALSE)

###
# Add final forecast to Historical Data
###
# Create new dataframe based on 'data' dataframe and then rbind

# pick any chunk of data dataframe with same size as horizon
forecastDF <- tail(data, horizon)
forecastDF[c(5)] <- unclass(c(forecast_oneQuarter$mean))
forecastDF$ObservationDate <- as.yearqtr(time(forecast_oneQuarter$mean))

data1 <- rbind(unclass(data), forecastDF)

colnames(data1) <- c("SeriesName", "DateAnalysis", "ETSmodel", "ObservationDate", "RawData", "Key1")
write.table(data1, file = paste(forecast_dir, Key1, "Historical_Forecasts.csv", sep="_"), sep =",",row.names = FALSE)

} 

############# END LOOP ##############
############# END LOOP ##############
############# END LOOP ##############