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
library(data.table)
library(lubridate)
library(stringr)
library(zoo)
library(dplyr)

##############################
# Possible analyses
##############################

figures_dir  <- "output_qt/figures/"
analyse_dir  <- "output_qt/analyses/"
forecast_dir <- "output_qt/forecasts/"

# remove files
do.call(file.remove, list(list.files(analyse_dir, full.names = TRUE)))

###
# Combine all forecasts
###

files <- list.files(forecast_dir, pattern = "final_forecasts.*\\.csv$", full.names = TRUE)
initial_df <- read.csv(files[1])

# Merge data frames using a loop
for (fl in files[2:length(files)]) {
  file_df <- read.csv(fl)
  initial_df <- rbind(initial_df, file_df)
}

# View the merged data frame
print(initial_df)

write.table(initial_df, file = paste0(analyse_dir, "combined_final_forecasts.csv"), sep =",",row.names = FALSE)


######################
# Type of model for each analysis
######################

fun_ETS_Used <- function(){

    files_Raw  <- list.files(forecast_dir, pattern = "Historical_Forecasts\\.csv$", full.names = TRUE)
    initial_df <- read.csv(files_Raw[1])[1,c(3,1)]

    # Merge data frames using a loop

    for (fl in files_Raw[2:length(files_Raw)]) {
    file_df <- read.csv(fl)
    initial_df <- rbind(initial_df, file_df[1,c(3,1)])
    } 

    write.table(initial_df, file = paste0(analyse_dir, "combined_model_used.csv"), sep =",",row.names = FALSE)
}

fun_ETS_Used()

######################
# Percentage Changes
######################

fun_percentage_change <- function(){

    files_Raw  <- list.files(forecast_dir, pattern = "Historical_Forecasts\\.csv$", full.names = TRUE)
    initial_df <- read.csv(files_Raw[1])[,c(1,4,5)]

    initial_df <- initial_df |> mutate(growth_monthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 1) * 100)
    initial_df <- initial_df |> mutate(growth_twomonthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 2) * 100)
    initial_df <- initial_df |> mutate(growth_threemonthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 3) * 100)
    initial_df <- initial_df |> mutate(growth_yearbefore = (RawData - dplyr::lag(RawData, 12))/dplyr::lag(RawData, 12) * 100)
    initial_df <- initial_df |> mutate(growth_fouryearbefore = (RawData - dplyr::lag(RawData, 48))/dplyr::lag(RawData, 48) * 100)
    
    # Merge data frames using a loop

    for (fl in files_Raw[2:length(files_Raw)]) {
       
        nextFile <- fl
        file_df <- read.csv(nextFile)[,c(1,4,5)]

        file_df <- file_df |> mutate(growth_monthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 1) * 100)
        file_df <- file_df |> mutate(growth_twomonthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 2) * 100)
        file_df <- file_df |> mutate(growth_threemonthbefore = (RawData - dplyr::lag(RawData, 1))/dplyr::lag(RawData, 2) * 100)
        file_df <- file_df |> mutate(growth_yearbefore = (RawData - dplyr::lag(RawData, 12))/dplyr::lag(RawData, 12) * 100)
        file_df <- file_df |> mutate(growth_fouryearbefore = (RawData - dplyr::lag(RawData, 48))/dplyr::lag(RawData, 48) * 100)

        initial_df <- rbind(initial_df, file_df)

    } 

    write.table(initial_df, file = paste0(analyse_dir, "combined_percentageChanges.csv"), sep =",",row.names = FALSE)
}

fun_percentage_change()

###
# Biggest movers, current month as starting point 
percentFile <- paste0(analyse_dir, "combined_percentageChanges.csv")
percent_df <- read.csv(percentFile)
percent_movers <- percent_df[percent_df$ObservationDate %like% format(Sys.Date(), "%Y %Q"), ]

write.table(percent_movers, file = paste0(analyse_dir, "combined_percentMovers_newMonth.csv"), sep =",",row.names = FALSE)

##### NOT IMPLEMENTED YET
######################
# Historical data plus level forecasts
######################

### Horizons
horizon <- 1  # should be 1 in general, from forecast file

rawDataFile <- "output_combined/a0_combinedQuarterly.csv"
combinedFinalForecasts <- "output_qt/analyses/combined_final_forecasts.csv"
output <- "output_qt/analyses/"

fun_combine_hist_forecast <- function(){ 

    data <- read.csv(rawDataFile)
    data$X <- as.Date(data$X)
    rownames(data) <- data$X
    
    # dimensions
    print(dim(data))

    finalForecasts <- read.csv(combinedFinalForecasts)
    finalForecasts$featureNames <- str_sub(finalForecasts$Key1, 12)
    finalForecasts$X <- as.Date(as.yearqtr(finalForecasts$Forecast_Period))

    f1 <- finalForecasts[c('Point.Forecast','featureNames','X')]

    f2 <- f1 |> 
    pivot_wider(names_from = featureNames, 
                values_from = Point.Forecast)

    
    # data (historical)
    f2 <- as.data.frame(f2)
    f2 <- f2[names(data)]
    f3 <- f2[order(f2$X),]
    rownames(f3) <- f3$X

    replaceThese <- which(is.na(data[nrow(data), ]), arr.ind=TRUE)
    lastDate <- data[nrow(data), 'X']

    for (i in as.numeric(replaceThese[, 2])) {
        data[nrow(data), i] <- f3[nrow(f3)-1, i]
    }

    output1 <- rbind(data, tail(f3,1))

    write.table(output1, file = paste0(output, "combined_historical_forecasts_levels.csv"), sep =",",row.names = FALSE)

}

fun_combine_hist_forecast()
