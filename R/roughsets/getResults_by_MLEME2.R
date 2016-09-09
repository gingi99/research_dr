## MLEM2によるルール抽出による推定結果を返す関数
getResults_by_MLEM2 <- function(kFilenames = c("iris"), 
                                kIter1 = 2,
                                kIter2 = 5,
                                kms = 0,
                                kmr = 0,
                                mgs = "max",
                                rpm = "Merged",
                                k = 3){
  library(readr)
  library(RoughSets)
  library(compiler)
  kIter  <- kIter1*kIter2
  results <- list()
  for(fn in kFilenames){
    results.fn <- list()
    for(i in 1:kIter1){
      for(j in 1:kIter2){
        print(paste("fn:",fn," i:", i," j:",j, sep=""))
        
        data.train <- read_tsv(paste("/data/uci/",fn,"/",fn,"-train",i,"-",j,".tsv", sep=""))
        data.train <- na.omit(data.train)
        data.test  <- read_tsv(paste("/data/uci/",fn,"/",fn,"-test",i,"-",j,".tsv", sep=""))
        data.test  <- na.omit(data.test)
        data.nominal <- read.csv(paste("/data/uci/",fn,"/",fn,".nominal", sep=""), sep=",", header=F)
        data.nominal <- as.vector(as.matrix(data.nominal))
        
        
        ## Incert multiple Sample
        # source("~/research_dr/createData/InsertSample.R")
        #data.train <- insertNewValueToData(data.train, 100)
        #data.train <- insertNewSampleToData(data.train, 1000)
        
        ## PP Cluster
        #source("~/R/ppdm/cluster.R")
        #data.train <- ppCluster(data.train, 
        #                        merged.number = kms, 
        #                        merged.rate   = kmr, 
        #                        merged.size   = mgs, 
        #                        rep.Method    = rpm)
        
        ## k_member_clustering
        #source("~/R/ppdm/k_member_clustering.R")
        #data.train <- get_k_member_df(data.train,
        #                              k = k,
        #                              merged.size = mgs,
        #                              rep.Method  = rpm)
        
        ## measure
        source("~/ppdm/get_PPDM_Measure.R")
        kano <- calKAnonymity(data.train)
        
        ## convert decisicon table class
        ## indx.nominalを自動的に決めれないか
        data.train   <- SF.asDecisionTable(data.train, decision.attr=ncol(data.train), indx.nominal=data.nominal)
        #true.classes <- data.test[,ncol(data.test), with=F][[1]]
        true.classes <- data.test[,ncol(data.test)]
        #data.test    <- SF.asDecisionTable(data.test[,-ncol(data.test), with=FALSE])
        data.test    <- SF.asDecisionTable(data.test[,-ncol(data.test)])
        
        ## 条件属性の離散化(と同時に、DecisionTable & data.frame型になってる)
        source("~/roughsets/My.Discretization.R")
        source("~/roughsets/My.ObjectFactory.R")
        data.train <- D.discretization.RST(data.train,
                                           type.method = "convert.nominal")
        
        ## cut value 不要
        #cut.values <- D.discretization.RST(data.train,
        #                                   type.method = "unsupervised.quantiles",
        #                                   nOfIntervals = 3)
        #data.train <- SF.applyDecTable(data.train, cut.values)
        #data.test  <- SF.applyDecTable(data.test,  cut.values)
        
        ## rule induction from the training set:
        source("~/roughsets/Rules.RST.R")
        source("~/roughsets/My.RuleInduction.OtherFuncCollections.R")
        if(!file.exists(paste0("/data/uci/",fn,"/",fn,"-train",i,"-",j,"-rules",".RDS"))){
          My.RI.MLEM2Rules.RST.cmp <- cmpfun(My.RI.MLEM2Rules.RST)
          rules <- My.RI.MLEM2Rules.RST.cmp(data.train)
          saveRDS(rules, paste0("/data/uci/",fn,"/",fn,"-train",i,"-",j,"-rules",".RDS"))
        }else{
          rules <- readRDS(paste0("/data/uci/",fn,"/",fn,"-train",i,"-",j,"-rules",".RDS"))
        }

        # rule clsutering
        # source("~/research_dr/rule_clustering/RuleClustering.R")
        # rules <- get_rule_clustering(rules, k=k)
        
        #class(rules)
        #str(rules)
        
        ## predicitons for the test set:
        source("~/roughsets/LERS.R")
        pred.vals <- predict.LERS(rules, data.test)
        #pred.vals1 <- predict(rules, data.test, votingMethod = X.ruleStrength)
        #pred.vals2 <- predict(rules, data.test, votingMethod = X.laplace)
        #pred.vals3 <- predict(rules, data.test, votingMethod = X.rulesCounting)
        
        ## checking the accuracy of predictions:
        precision <- sprintf("%.3f", mean(pred.vals == true.classes))
        #precision <- c(sprintf("%.3f", mean(pred.vals1 == true.classes)), 
        #               sprintf("%.3f", mean(pred.vals2 == true.classes)),
        #               sprintf("%.3f", mean(pred.vals3 == true.classes)))      
        precision.sd <- sprintf("%.3f", sd(pred.vals == true.classes))
        source("~/ppdm/get_PPDM_Measure.R")
        entropy <- calEntropyForData(data.train)
        result <- paste(precision, "±", precision.sd, sep="")
        #result <- c(paste(sprintf("%.3f", mean(pred.vals1 == true.classes)),"±",sprintf("%.3f", sd(pred.vals1 == true.classes)), sep=""),
        #            paste(sprintf("%.3f", mean(pred.vals2 == true.classes)),"±",sprintf("%.3f", sd(pred.vals2 == true.classes)), sep=""),
        #            paste(sprintf("%.3f", mean(pred.vals3 == true.classes)),"±",sprintf("%.3f", sd(pred.vals3 == true.classes)), sep=""))
        
        ## append
        results.fn <- list.append(results.fn, 
                                  list(precision = precision, 
                                       precision_sd = precision.sd,
                                       entropy = entropy,
                                       kano = kano,
                                       result = result))
      }
    }
    for(i in kIter){
      names(results.fn) <- paste(fn,seq(1:kIter),sep="")
    }
    results <- list.append(results, results.fn)
  }
  names(results) <- kFilenames
  return(results)
}
