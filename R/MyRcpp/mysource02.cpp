#include <Rcpp.h>
using namespace Rcpp;

// [[Rcpp::export]]
int timesTwo(int x) {
   return x * 2;
}

NumericVector myFunc(NumericVector A){
   A[0]=100;
   NumericVector B=A;
   B[1]=200;
   return(A);
}

// [[Rcpp::export]]
List lapply1(List input, Function f) {
  int n = input.size();
  List out(n);

  for(int i = 0; i < n; i++) {
    out[i] = f(input[i]);
  }

  return out;
}
