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
library(lubridate)

# Time series plots
# https://cran.rstudio.com/web/packages/ggfortify/vignettes/plot_ts.html

forecast_dir <- "output_combinedMonthly/combinedMonthly_extended_ETS.csv"
output_dir <- "output_combined/"

# Model consists of three letters following Hyndman (2008) and here: https://search.r-project.org/CRAN/refmans/forecast/html/ets.html

# First letter is the error type:     A, M or Z
# Second letter is the trend type:    N, A, M, Z
# Third letter is the season type:    N, A, M, Z

# Some of the models have names:
#     ANN is simple exponential smoothing with additive errors.
#     MAM is multiplicative Holt-Winters with multiplicative errors.


##########################

### Horizons
horizon <- 6

# load data
dt1 <- read.csv("output_combined/a0_combinedQuarterly.csv", sep = ",")

allColumns <- colnames(dt1)

##########################
# FOR LOOP
##########################
dfList <- list()

for(colName in allColumns){ 

  #dont want to forecast date
  if (colName == "X") {next}

  #colName <- "gdp_total"

  print(colName)

  # Key1 connects all the data
  Key1 <- paste(Sys.Date(), "_", colName, sep="")

  series1 <- ts(dt1[colName], frequency = 4, start=c(1995,1))

  # if missing many values, flag it
  if (sum(is.na(series1)) > 20) {   ###### This is effectively not a constraint when set so high
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

  ####################
  # final forecast
  ####################

  fit <- ets(series1, model=modelform, damped=FALSE)
  forecast_months <- forecast(fit, h = horizon)
  forecast1 <- forecast_months$mean

  merged_ts <- ts(c(series1, forecast1), start = start(series1), frequency = frequency(series1)) 

  df_data <- data.frame(colName =as.matrix(merged_ts), date=as.Date(as.yearmon(time(merged_ts))))

  colnames(df_data) <- c(colName, "date")

  dfList[[colName]] <- df_data
} 

############# END LOOP ##############
############# END LOOP ##############
############# END LOOP ##############

#put all data frames into list
#merge all data frames in list
df_final <- dfList %>% reduce(full_join, by='date') 

rownames(df_final) <- df_final$date
df_final$date <- NULL

write.csv(df_final, file = paste0(output_dir, "a0_combinedQuarterly_extended_ETS.csv"),fileEncoding="UTF-8")
