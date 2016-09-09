## 下近似集合を返す

# ---------------------
# パッケージ
# ---------------------
library(readr)
library(RoughSets)
library(compiler)

# ---------------------
# パラメータ
# ---------------------
kFilenames <- c("nursery")
kIter1 <- 10
kIter2 <- 10
  
kIter  <- kIter1*kIter2
for(fn in kFilenames){
  for(i in 1:kIter1){
    for(j in 1:kIter2){
      print(paste0("START : fn:",fn," i:", i," j:",j)) 
      data.train <- read_tsv(paste("/data/uci/",fn,"/",fn,"-train",i,"-",j,".tsv", sep=""))
      data.train <- na.omit(data.train)
      data.nominal <- read.csv(paste("/data/uci/",fn,"/",fn,".nominal", sep=""), sep=",", header=F)
      data.nominal <- as.vector(as.matrix(data.nominal))
        
      # convert decisicon table class
      # indx.nominalを自動的に決めれないか
      data.train   <- SF.asDecisionTable(data.train, decision.attr=ncol(data.train), indx.nominal=data.nominal)
        
      # 条件属性の離散化(と同時に、DecisionTable & data.frame型になってる)
      source("~/roughsets/My.Discretization.R")
      source("~/roughsets/My.ObjectFactory.R")
      data.train <- D.discretization.RST(data.train,
                                        type.method = "convert.nominal")
        
      source("~/roughsets/Rules.RST.R")
      source("~/roughsets/My.RuleInduction.OtherFuncCollections.R")
      
      decision.table <- data.train
        
      if (!inherits(decision.table, "DecisionTable")) {
        stop("Provided data should inherit from the \'DecisionTable\' class.")
      }
      if(is.null(attr(decision.table, "decision.attr"))) {
        stop("A decision attribute is not indicated.")
      } else {
        # 決定属性がある列を求める（irisなら5）
        decIdx = attr(decision.table, "decision.attr")
      }
        
      # 決定属性の決定クラスのFactor型ベクトルを求める（irisなら、決定クラス150要素）
      clsVec <- dplyr::select(decision.table, decIdx)[[1]]
        
      # ユニークな決定クラスを求める（irisなら、setosa、versicolor、virginicaの3つ） 
      uniqueCls <- unique(clsVec)
        
      # 決定属性の列名を求める（irisなら、"Species"）
      decisionName <- colnames(decision.table)[decIdx]
        
      # 各決定クラスの度数を求める（irisなら、50,50,50）
      clsFreqs <- table(clsVec)
        
      # 識別不能関係のリストを返す
      INDrelation = BC.IND.relation.RST(decision.table, (1:ncol(decision.table))[-decIdx])
        
      # 各決定クラスの上下近似を求める
      approximations = BC.LU.approximation.RST(decision.table, INDrelation)
      lowerApproximations = approximations$lower.approximation
        
      # 下近似を保存 (ind を 1引いてるのは、python側のindexと揃える = 0始まりにするため)
      lapply(names(lowerApproximations), function(i){
        return(data.frame(ind = (unname(lowerApproximations[[i]]) - 1), class = i))
      }) %>% list.stack() -> df.la
      
      # save
      write.table(df.la, 
                  paste0("/data/uci/",fn,"/",fn,"-train-la-",i,"-",j,".tsv"), 
                  sep='\t',row.names = F, quote =F)
      # 下近似だけを使うので残りを削除
      rm(INDrelation, approximations)
      
      # END
      print(paste0("END : fn:",fn," i:", i," j:",j)) 
    }
  }
}