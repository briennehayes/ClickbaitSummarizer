library(rjson)
library(dplyr)

buzzfeed <- fromJSON(file = "Data/buzzfeed.json")
nytimes <- fromJSON(file = "Data/nytimes.json")

list_to_df <- function(l){
  return(data.frame(matrix(unlist(l), nrow = length(l), byrow = T), stringsAsFactors=FALSE))
}

buzzfeed_df <- list_to_df(buzzfeed)[, 1:2]
nytimes_df <- list_to_df(nytimes)[, 1:2]

buzzfeed_sample <- sample_n(buzzfeed_df, 367)
nytimes_sample <- sample_n(nytimes_df, 367)

df <- rbind(buzzfeed_sample, nytimes_sample) %>%
  sample_frac(1L) %>%
  select(X1)

write.csv(df, "Data/eval_headlines.csv")