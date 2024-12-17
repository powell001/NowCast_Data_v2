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

figures_dir  <- "output_mo/figures/"
forecasts_dir <- "output_mo/forecasts/"
analyse_dir  <- "output_mo/analyses/"


# Model consists of three letters following Hyndman (2008) and here: https://search.r-project.org/CRAN/refmans/forecast/html/ets.html

# First letter is the error type:     A, M or Z
# Second letter is the trend type:    N, A, M, Z
# Third letter is the season type:    N, A, M, Z

# Some of the models have names:
#     ANN is simple exponential smoothing with additive errors.
#     MAM is multiplicative Holt-Winters with multiplicative errors.


####################################
horizon1 <- 12
finalforecastHorizon <- 1
####################################

appropriateModels <- c("ANNX", "ANAX", "ANMX",
                       "AANX", "AAAX", "AAMX",
                       "AAND", "AAAD", "ANMD",
                       "AMNX", "AMAX", "AMMX",
                       "AMND", "AMAD", "AMMD",
                       "MNNX", "MNAX", "MNMX",
                       "MANX", "MAAX", "MAMX",
                       "MAND", "MAAD", "MNMD",
                       "MMNX", "MMAX", "MMMX",
                       "MMND", "MMAD", "MMMD"
                       )


# load data
dt1 <- read.csv("output_combined/a0_combinedMonthly.csv", sep = ",")

rownames(dt1) <- dt1$X
colnames(dt1)
dim(dt1)
allColumns <- colnames(dt1)
# remove perioden column
data_columns <- allColumns[c(-1)]

# remove files
do.call(file.remove, list(list.files(forecast_dir, full.names = TRUE)))
do.call(file.remove, list(list.files(figures_dir, full.names = TRUE)))

##########################
# ending date
##########################
start_date <- "1995-01-01"
mystart = c(1995,1,1)
end_date <- "2024-10-01"

dt1 %>% filter(rownames(dt1) >= start_date &  rownames(dt1) <= end_date) -> dt1

##########################
##########################
##########################

##########################
# FOR LOOP
##########################


for(colName in data_columns){ 

  print(colName)

  # test case
  #colName <- "gdp_total"

  # connects all the data
  Key1 <- paste(Sys.Date(), "_", colName, sep="")

  series1 <- ts(dt1[colName], frequency = 12, start=mystart)
  series1 <- na.omit(series1)

  #########################
  # Which model to use
  #########################

  bestMod <- function(appropriateModels, data, lowest_aic = Inf){

      for (mod in appropriateModels){

      tryCatch({

          ##############################
          #print(mod)  

          error1 <- str_sub(mod, 1, 1)
          trend2 <- str_sub(mod, 2, 2)
          season3 <- str_sub(mod, 3, 3)
          damp4 <- str_sub(mod, 4, 4)
          ##############################

      if(damp4 == "X"){ #damped is FALSE
              model <- ets(data, model = mod, damped = FALSE)
              out1 <- list(mod, model$aic, damped = FALSE)

              } else { #damped is TRUE
                  model <- ets(data, model = mod, damped = TRUE)

                  out1 <- list(mod, model$aic, damped = TRUE)
                  #print(out1[[2]])
              }
      }, error=function(e){cat("ERROR :",conditionMessage(e), "\n")})    

      new_aic <- out1[[2]]

      if (new_aic < lowest_aic){
          lowest_aic <- out1[[2]]
          best_model <- out1
      }
      }

      bm_df <- t(as.data.frame(matrix(unlist(best_model)),nrow=1,ncol=3))  

      colnames(bm_df) <- c("Model", "AIC", "Damped")
      rownames(bm_df) <- c("model")

      return(bm_df)
  }

  #########################
  # Which model to use
  #########################

  choosenModel <- bestMod(appropriateModels, series1)
  modelform <- choosenModel[1,1]
  dampform  <- choosenModel[1,3]

  if(dampform == "FALSE"){
    fit <- ets(series1, model=modelform, damped=FALSE)
  } else {
    fit <- ets(series1, model=modelform, damped=TRUE)
  }
  
  train <- head(series1, round(length(series1) - horizon1))
  test <- tail(series1, horizon1)

   if(dampform == "FALSE"){
    fit <- ets(train, model=modelform, damped=FALSE)
  } else {
    fit <- ets(train, model=modelform, damped=TRUE)
  }
  forecasted1 <- forecast(fit, h=horizon1)

  png(filename=paste(figures_dir, Key1, "TrainTestForecast.png", sep = "_"))
  print(autoplot(forecasted1, include=horizon1+2) + autolayer(test) + ggtitle(colName))
  dev.off()

  ####################
  # final forecast
  ####################

  if(dampform == "FALSE"){
    fit <- ets(series1, model=modelform, damped=FALSE)
  } else {
    fit <- ets(series1, model=modelform, damped=TRUE)
  }

  forecast_oneMonth <- forecast(fit, h=finalforecastHorizon)

  png(filename=paste(figures_dir, Key1, "final_forecasts.png", sep = "_"))
  print(autoplot(tail(series1, 2)) + autolayer(forecast_oneMonth) + ggtitle(colName))
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
    ObservationDate = as.yearmon(time(series1)),
    RawData = series1
  )
  data$Key1 <- Key1

  colnames(data) <- c("SeriesName", "DateAnalysis", "ETSmodel", "ObservationDate", "RawData", "Key1")

  write.table(data, file = paste(forecasts_dir, Key1, "RawData.csv", sep="_"), sep =",",row.names = FALSE)

  ###
  # TrainTestForecast
  ###
  forecast_tibble <- as.data.frame(forecasted1)
  forecast_tibble$Key1 <- Key1 

  write.table(forecast_tibble, file = paste(forecasts_dir, Key1, "TrainTestForecast.csv", sep="_"), sep =",",row.names = FALSE)

  ###
  # finalForecast
  ###
  forecast_oneMonth <- forecast(fit, h=finalforecastHorizon)
  finalForecast <- as.data.frame(forecast_oneMonth, row.names = NULL)
  finalForecast$Key1 <- Key1
  finalForecast <- tibble::rownames_to_column(finalForecast, "Forecast_Period")  

  write.table(finalForecast, file = paste(forecasts_dir, Key1, "final_forecasts.csv", sep="_"), sep =",",row.names = FALSE)

  
###
# Add final forecast to Historical Data
###
# Create new dataframe based on 'data' dataframe and then rbind

# pick any chunk of data dataframe with same size as horizon
forecastDF <- tail(data, horizon)
forecastDF[c(5)] <- unclass(c(forecast_oneMonth$mean))
forecastDF$ObservationDate <- as.yearmon(time(forecast_oneMonth$mean))

data1 <- rbind(unclass(data), forecastDF)

colnames(data1) <- c("SeriesName", "DateAnalysis", "ETSmodel", "ObservationDate", "RawData", "Key1")
write.table(data1, file = paste(forecast_dir, Key1, "Historical_Forecasts.csv", sep="_"), sep =",",row.names = FALSE)


} 


############# END LOOP ##############
############# END LOOP ##############
############# END LOOP ##############

