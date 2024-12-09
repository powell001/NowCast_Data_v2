{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "vscode": {
     "languageId": "r"
    }
   },
   "outputs": [],
   "source": [
    "library(reshape2)\n",
    "library(rsdmx)\n",
    "library(tidyr)\n",
    "\n",
    "output <- \"../output_mo_qt/\"\n",
    "myUrl <- \"https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,4.1/NLD.M.LOCOS3+LOCOPC+CCICP+BCICP......H?startPeriod=1995-01&dimensionAtObservation=AllDimensions\"\n",
    "\n",
    "dataset <- readSDMX(myUrl)\n",
    "stats <- as.data.frame(dataset)\n",
    "\n",
    "\n",
    "#write.csv(stats,\"output/LeadingIndicators_NLD_m0.csv\", row.names = FALSE)\n",
    "\n",
    "#stats[order(stats$TIME_PERIOD),]\n",
    "\n",
    "head(nld1)\n",
    "\n",
    "nld2 <- pivot_wider(nld1, names_from=MEASURE, values_from=obsValue)\n",
    "\n",
    "nld2$TIME_PERIOD <- as.Date(paste0(nld2$TIME_PERIOD, \"-01\"), format = \"%Y-%m-%d\")\n",
    "\n",
    "nld3 <- nld2[order(nld2$TIME_PERIOD),]\n",
    "nld3$REF_AREA <- NULL\n",
    "\n",
    "names(nld3)[c(2,3)] <- paste0(names(nld3)[c(2,3)], \"_NLD_CLI\")\n",
    "tail(nld3)\n",
    "plot(ts(nld3[,c(2,3)]))\n",
    "myUrl <- \"https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,4.1/DEU.M.LOCOS3+LOCOPC+CCICP+BCICP......H?startPeriod=1995-01&dimensionAtObservation=AllDimensions\"\n",
    "\n",
    "dataset <- readSDMX(myUrl)\n",
    "stats <- as.data.frame(dataset)\n",
    "#stats[order(stats$TIME_PERIOD),]\n",
    "deu1 <- stats[c(\"TIME_PERIOD\", \"REF_AREA\", \"MEASURE\",\"obsValue\")]\n",
    "\n",
    "deu2 <- pivot_wider(deu1, names_from=MEASURE, values_from=obsValue)\n",
    "deu2$LOCOS3 <- NULL\n",
    "\n",
    "\n",
    "deu2$TIME_PERIOD <- as.Date(paste0(deu2$TIME_PERIOD, \"-01\"), format = \"%Y-%m-%d\")\n",
    "\n",
    "deu3 <- deu2[order(deu2$TIME_PERIOD),]\n",
    "deu3$REF_AREA <- NULL\n",
    "\n",
    "names(deu3)[c(2,3)] <- paste0(names(deu3)[c(2,3)], \"_DEU\")\n",
    "tail(deu3)\n",
    "plot(ts(deu3[,c(2,3)]))\n",
    "oecd_confidence <- merge(x = nld3, y = deu3, by = \"TIME_PERIOD\", all = TRUE)\n",
    "write.csv(oecd_confidence, paste0(output, \"OECD_Confidence_mo.csv\"), row.names = FALSE)\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "R",
   "language": "R",
   "name": "ir"
  },
  "language_info": {
   "codemirror_mode": "r",
   "file_extension": ".r",
   "mimetype": "text/x-r-source",
   "name": "R",
   "pygments_lexer": "r",
   "version": "4.4.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
