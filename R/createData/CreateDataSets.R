## Packages
library(data.table)
library(dplyr)
library(readr)

## Data Sets
### iris
head(iris)
#write.table(iris, "/data/iris.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### adult
adult <- fread("/data/uci/adult/adult.tsv")
#write.table(adult, "/data/uci/adult/adult.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### bank
bank <- fread("/data/uci/bank/origin/bank-full.csv")
#write.table(bank, "/data/uci/bank/bank.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### car
car <- fread("/data/uci/car/car.tsv")
head(car)
#write.table(car, "/data/uci/car/car.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### dermatology
dermatology <- fread("/data/uci/dermatology/dermatology.tsv")
head(dermatology)
#write.table(dermatology, "/data/uci/dermatology/dermatology.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### ecoli
ecoli <- fread("/data/uci/ecoli/ecoli.tsv")
head(ecoli)
#write.table(ecoli, "/data/uci/ecoli/ecoli.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### glass
glass <- fread("/data/uci/glass/glass.tsv")
head(glass)
#write.table(glass, "/data/uci/glass/glass.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### hayes.roth
hayes.roth <- fread("/data/uci/hayes-roth/hayes.roth.tsv")
head(hayes.roth)
#write.table(hayes.roth, "/data/uci/hayes-roth/hayes.roth.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### image
image <- fread("/data/uci/image/image.tsv")
head(image)
#write.table(image, "/data/uci/image/image.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### imports85
imports85 <- fread("/data/uci/imports-85/imports-85.tsv")
head(imports85)
#write.table(imports85, "/data/uci/imports-85/imports-85.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### new.thyroid
new.thyroid <- fread("/data/uci/new-thyroid/new-thyroid.tsv")
head(new.thyroid)
#write.table(new.thyroid, "/data/uci/new-thyroid/new-thyroid.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### nursery
nursery <- fread("/data/uci/nursery/nursery.tsv")
head(nursery)
#write.table(nursery, "/data/uci/nursery/nursery.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### optdigits_c
optdigits_c <- fread("/data/uci/optdigits/optdigits_c.tsv")
head(optdigits_c)
#write.table(optdigits_c, "/data/uci/optdigits/optdigits_c.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### page-blocks
page.blocks <- fread("/data/uci/page-blocks/page-blocks.tsv")
head(page.blocks)
#write.table(page.blocks, "/data/uci/page-blocks/page-blocks.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### soybeans-large
soybean.large <- fread("/data/uci/soybean/soybean-large.tsv")
head(soybean.large)
#write.table(soybean.large, "/data/uci/soybean/soybean-large.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### splice
splice <- fread("/data/uci/splice/splice.tsv")
head(splice)
#write.table(splice, "/data/uci/splice/splice.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### vehicle
vehicle <- fread("/data/uci/vehicle/vehicle.tsv")
head(vehicle)
#write.table(vehicle, "/data/uci/vehicle/vehicle.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### vowel-context
vowel_context <- fread("/data/uci/vowel-context/vowel-context.tsv")
head(vowel_context)
#write.table(vowel_context, "/data/uci/vowel-context/vowel-context.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### wine
wine <- fread("/data/uci/wine/wine.tsv")
head(wine)
#write.table(wine, "/data/uci/wine/wine.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### yeast
yeast <- fread("/data/uci/yeast/yeast.tsv")
head(yeast)
#write.table(yeast, "/data/uci/yeast/yeast.tsv", sep="\t", quote=FALSE, row.names=FALSE)

### zoo
zoo <- fread("/data/uci/zoo/zoo.tsv")
head(zoo)
#write.table(zoo, "/data/uci/zoo/zoo.tsv", sep="\t", quote=FALSE, row.names=FALSE)

## Create Data for Cross Validation
### 10 fold cross validationのために、n分割して、訓練用・テスト用データセットを10個作る
### それをm回行えるように、合計100個のデータ・セットを作る

createDataForCrossValidation <- function(filename, n, m){
  for(iteration in 1:m){
    data <- fread(filename)
    k <- n #分割数
    Nresidual <- k-nrow(data)%%k
    dummyData <- as.data.frame(matrix(NA,nrow=Nresidual,ncol=ncol(data)))
    names(dummyData) <- names(data)
    sampleData <- bind_rows(data, dummyData) 
    splitData <- split(sampleData, 1:k)
    for(i in 1:k){
      trainData <- data.frame()
      testData <- data.frame()
      for(j in 1:k){
        if(i == j){
          testData <- as.data.frame(splitData[j])
          names(testData) <- names(data)
        }else{
          trainData_tmp <- as.data.frame(splitData[j])
          names(trainData_tmp) <- names(data)
          trainData <- bind_rows(trainData, trainData_tmp)
        }
      }
      filepath <- strsplit(filename, ".tsv")
      write.table(testData, paste(filepath, "-test",iteration,"-", i, ".tsv", sep=""), sep="\t", quote=FALSE, row.names=FALSE)
      write.table(trainData, paste(filepath, "-train",iteration,"-", i, ".tsv", sep=""), sep="\t", quote=FALSE, row.names=FALSE)
    }
  }
}
#createDataForCrossValidation("/data/uci/bank/bank.tsv", 10, 10)

## Adult's data cleansing
adult <- fread("/data/uci/adult/adult.tsv")
adult2 <- dplyr::select(adult, age, workclass, education, marital_status, occupation, race, sex, native_country, class)
#adult2$age <- (adult2$age - mean(adult2$age, na.rm = T)) / sd(adult2$age, na.rm = T)
adult2$age <- (adult2$age - min(adult2$age, na.rm = T)) / (max(adult2$age, na.rm = T) - min(adult2$age, na.rm = T))
#write.table(adult2, "/data/uci/adult/adult_cleansing.tsv", sep="\t", quote=FALSE, row.names=FALSE)

## Adult's data cleansing for age
adult3 <- dplyr::select(adult, age, workclass, education, marital_status, occupation, race, sex, native_country, class)
age2 <- cut(adult3$age, breaks=c(10,20,30,40,50,60,70,80,90), labels=c("10s","20s", "30s", "40s", "50s", "60s", "70s", "80s"), right=F, include.lowest=T)
adult3 <- mutate(adult3, age = age2)
#write.table(adult3, "/data/uci/adult_cleansing2/adult_cleansing2.tsv", sep="\t", quote=FALSE, row.names=FALSE)

## German Credit data cleansing
credit_categorical <- fread("/mnt/data/uci/german_credit/german_credit.tsv")
credit_categorical$Duration_of_Credit_month <- cut(credit_categorical$Duration_of_Credit_month, breaks=c(0,6,12,18,24,30,36,42,48,54), right = TRUE, include.lowest = TRUE)
credit_categorical$Credit_Amount <- cut(credit_categorical$Credit_Amount,breaks=c(0,500,1000,1500,2500,5000,7500,10000,15000,20000), right = TRUE, include.lowest = TRUE)
credit_categorical$Age_years <- cut(credit_categorical$Age_years, breaks=c(0,25,39,59,64,65,999), right = TRUE, include.lowest = TRUE)
write.table(credit_categorical, "/mnt/data/uci/german_credit_categorical/german_credit_categorical.tsv", sep="\t", quote=FALSE, row.names=FALSE)
