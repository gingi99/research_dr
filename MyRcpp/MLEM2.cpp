#include <Rcpp.h>
using namespace Rcpp;

// [[Rcpp::export]]
NumericVector cover_num(List TG, NumericVector uncoveredConcept_unname) {
   int len = TG.size();
   NumericVector out(len);
   for(int i=0; i<len; i++){
     List tg = TG[i];
     NumericVector supports = tg["support"];
     out[i] = intersect(supports, uncoveredConcept_unname).size();
   }
   return(out);
}
