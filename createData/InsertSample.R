## Insert
### Insert random value to row 
#### insertNewValueToData関数を定義。data.frameに変換が必要なのが注意
#### 各属性のブートストラップサンプルを生成して、元データにbindする

insertNewValueToData <- function(data, sample_number){
  v <- as.list(NULL)
  inse.data <- as.data.frame(data)
  n <- sample_number
  set.seed(20)
  for(i in 1:length(inse.data)){
    assign(paste("n", i, sep=""), sample(inse.data[,i], n, replace = TRUE))
    v <- c(v, list(get(paste("n", i, sep=""))))
  }
  inserted.data <- data.frame(v)
  names(inserted.data) <- names(inse.data)
  newdata <- rbind_list(inse.data, inserted.data)
  return(newdata)
}
#iris <- fread("/data/uci/iris/iris.tsv")
#newiris <- insertNewValueToData(as.data.frame(iris), 100)

### Insert random sample to row
#### insertNewSampleToData関数を定義。data.frameに変換が必要なのが注意
#### 各サンプルのブートストラップサンプルを生成して、元データにbindする
#### データ内のサンプルから重複を許して、指定した数だけinsertする

insertNewSampleToData <- function(data, sample_number){
  v <- as.list(NULL)
  inse.data <- data
  set.seed(20)
  rownumbers <- sample(nrow(inse.data), sample_number, replace = TRUE)
  newdata <- inse.data[rownumbers,]
  newdata <- rbind_list(inse.data, newdata)
  return(newdata)
}
#iris <- fread("/data/uci/iris/iris.tsv")
#newiris <- insertNewSampleToData(as.data.frame(iris), 100)
