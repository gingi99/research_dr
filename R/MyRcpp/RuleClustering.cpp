#include <Rcpp.h>
using namespace Rcpp;

// [[Rcpp::export]]
String convert_df_from_rules_Rcpp(List rules) {
   StringVector condition_attr = rules.attr("colnames");
   String decision_attr = rules.attr("dec.attr");
   for(List::iterator it = rules.begin(); it != rules.end(); ++it){
      List rule = *it;
      NumericVector idx = rule["idx"];
      StringVector values = rule["values"];
      //NumericVector idx = as<NumericVector>it["idx"];
      //values <- rule$values
   }
   return(decision_attr);
}

// [[Rcpp::export]]
NumericMatrix cal_dist_rules_Rcpp(DataFrame df, List list_df){
  NumericMatrix mat_df_dist(df.nrows(), df.nrows());
  Function dist_kusunoki_Rcpp("dist_kusunoki_Rcpp"); 
  for(int i=0; i < (df.nrows()-1); i++){
    for(int j=(i+1); j < df.nrows(); j++){
      List x = list_df[i];
      List y = list_df[j];
      mat_df_dist(i,j) = as<double>(dist_kusunoki_Rcpp(x,y));
      mat_df_dist(j,i) = as<double>(dist_kusunoki_Rcpp(x,y));
    }
  }
  return(mat_df_dist);
}

// [[Rcpp::export]]
double dist_kusunoki_Rcpp(List x, List y) {
   double len = x.length();
   double ans = 0.0;
   for(int i=0; i < len; i++) {
     // 型の判定の仕方がわからない
     
     // numeric の場合
     //double xx = x[i];
     //double yy = y[i];
    
     // String の場合
     if(StringVector::is_na(x[i]) && StringVector::is_na(y[i])){
       ans = ans;
     }
     else{
       if(StringVector::is_na(x[i]) || StringVector::is_na(y[i])){
          ans = ans + 1.0;
       }
       else{
         std::string xx = Rcpp::as<std::string>(x[i]);
         std::string yy = Rcpp::as<std::string>(y[i]);
         if(xx == yy){
           ans = ans;
         }else{
           ans = ans + 1.0;
         }
       }
     }
   }
   return(ans / len);
}

// [[Rcpp::export]]
LogicalVector is_naC(NumericVector x) {
  int n = x.size();
  LogicalVector out(n);

  for (int i = 0; i < n; ++i) {
    out[i] = NumericVector::is_na(x[i]);
  }
  return out;
}

// [[Rcpp::export]]
int f4(List x) {
  int n = x.size();

  for(int i = 0; i < n; ++i) {
    LogicalVector res = x[i] * 2;
    if (res[0]) return i + 1;
  }
  return 0;
}

// [[Rcpp::export]]
List attribs(List out) {
  out.names() = CharacterVector::create("a", "b", "c");
  out.attr("my-attr") = "my-value";
  out.attr("class") = "my-class";
  return (out);
}
