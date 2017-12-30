function logProb = lm_prob(sentence, LM, type, delta, vocabSize)
%
%  lm_prob
% 
%  This function computes the LOG probability of a sentence, given a 
%  language model and whether or not to apply add-delta smoothing
%
%  INPUTS:
%
%       sentence  : (string) The sentence whose probability we wish
%                            to compute
%       LM        : (variable) the LM structure (not the filename)
%       type      : (string) either '' (default) or 'smooth' for add-delta smoothing
%       delta     : (float) smoothing parameter where 0<delta<=1 
%       vocabSize : (integer) the number of words in the vocabulary
%
% Template (c) 2011 Frank Rudzicz

  logProb = -Inf;

  % some rudimentary parameter checking
  if (nargin < 2)
    disp( 'lm_prob takes at least 2 parameters');
    return;
  elseif nargin == 2
    type = '';
    delta = 0;
    vocabSize = length(fieldnames(LM.uni));
  end
  if (isempty(type))
    delta = 0;
    vocabSize = length(fieldnames(LM.uni));
  elseif strcmp(type, 'smooth')
    if (nargin < 5)  
      disp( 'lm_prob: if you specify smoothing, you need all 5 parameters');
      return;
    end
    if (delta <= 0) or (delta > 1.0)
      disp( 'lm_prob: you must specify 0 < delta <= 1.0');
      return;
    end
  else
    disp( 'type must be either '''' or ''smooth''' );
    return;
  end

  words = strsplit(' ', sentence);

  % TODO: the student implements the following
  % TODO: once upon a time there was a curmudgeonly orangutan named Jub-Jub.
  logProb = 0;
  for w=2:length(words)
      bigram_prob = -Inf;
      if isfield(LM.uni, words{w-1}) == 0
          % impossible MLE unless smoothing
          if (delta * vocabSize) > 0
              bigram_prob = log2(delta / (delta * vocabSize));
          else
              bigram_prob = -Inf;
          end
      else
          if isfield(LM.bi.(words{w-1}), words{w}) == 0
              if (delta * vocabSize) > 0
                  bigram_prob = log2(delta / (delta * vocabSize + LM.uni.(words{w-1})));
              else
                  bigram_prob = -Inf;
              end
          else
              bigram_prob = log2((LM.bi.(words{w-1}).(words{w}) + delta)/(LM.uni.(words{w-1}) + (delta * vocabSize)));
          end
      end
      logProb = logProb + bigram_prob;
  end
return