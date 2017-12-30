function outSentence = preprocess( inSentence, language )
%
%  preprocess
%
%  This function preprocesses the input text according to language-specific rules.
%  Specifically, we separate contractions according to the source language, convert
%  all tokens to lower-case, and separate end-of-sentence punctuation 
%
%  INPUTS:
%       inSentence     : (string) the original sentence to be processed 
%                                 (e.g., a line from the Hansard)
%       language       : (string) either 'e' (English) or 'f' (French) 
%                                 according to the language of inSentence
%
%  OUTPUT:
%       outSentence    : (string) the modified sentence
%
%  Template (c) 2011 Frank Rudzicz 

  global CSC401_A2_DEFNS
  
  % first, convert the input sentence to lower-case and add sentence marks 
  inSentence = [CSC401_A2_DEFNS.SENTSTART ' ' lower( inSentence ) ' ' CSC401_A2_DEFNS.SENTEND];

  % trim whitespaces down 
  inSentence = regexprep( inSentence, '\s+', ' '); 

  % initialize outSentence
  outSentence = inSentence;

  % perform language-agnostic changes
  % TODO: your code here
  outSentence = regexprep( outSentence, '\.?', ' .');
  outSentence = regexprep( outSentence, '\,', ' ,');
  outSentence = regexprep( outSentence, '\??', ' ?');
  outSentence = regexprep( outSentence, '\:', ' :');
  outSentence = regexprep( outSentence, '\;', ' ;');
  outSentence = regexprep( outSentence, '\!?', ' !');
  outSentence = regexprep( outSentence, '\+', ' + ');
  outSentence = regexprep( outSentence, '\*', ' * ');
  outSentence = regexprep( outSentence, '\<', ' < ');
  outSentence = regexprep( outSentence, '\>', ' > ');
  outSentence = regexprep( outSentence, '\"', ' " ');
  outSentence = regexprep( outSentence, '\s+', ' ');
  
  %dealing with hyphens between parantheses
  betweenPar = regexpi(outSentence, '\(+\w*-+\w*\)+');
  %if there is text between parantheses
  if isempty(betweenPar) == 0
     %look for closing parantheses
     parEnd = strfind(outSentence(betweenPar:end), ')')';
     %look for the hyphen 
     hyphen = regexpi(outSentence(betweenPar:betweenPar + parEnd(1)), '-');
     %seperate the hyphen from the text
     outSentence = [outSentence(1:hyphen+betweenPar-2) ' ' outSentence(hyphen+betweenPar-1) ' ' outSentence(hyphen+betweenPar:end)];
  end
  
  %dealing with parantheses
  openPar = regexpi(outSentence, '\(');
  closePar = regexpi(outSentence, '\)');
  outSentence = regexprep(outSentence, '(\s*', '( ');
  outSentence = regexprep(outSentence, '\s*)', ' )');
  
  
  

  switch language
   case 'e'
    % TODO: your code here
    %clitics and possessives
    outSentence = regexprep(outSentence, '''s', ' ''s');
    outSentence = regexprep(outSentence, '''m', ' ''m');
    outSentence = regexprep(outSentence, 's''', 's ''');
    outSentence = regexprep(outSentence, 'n''t', ' n''t');
    outSentence = regexprep( outSentence, '\s+', ' ');
    
    
    

   case 'f'
    % TODO: your code here
    %singular definite article
    outSentence = regexprep(outSentence, 'l''', 'l'' ');
    %que
    outSentence = regexprep(outSentence, 'qu''', 'qu'' ');
    outSentence = regexprep(outSentence, 'd''accord', 'd''accord');
    outSentence = regexprep(outSentence, 'd''abord', 'd''abord');
    outSentence = regexprep(outSentence, 'd''ailleurs', 'd''ailleurs');
    outSentence = regexprep(outSentence, 'd''habitude', 'd''habitude');
    
    %single consonant words
    apostIndex =  regexpi(outSentence, '''\w+');
    for i = 1:length(apostIndex)
        if strcmp('d', outSentence(apostIndex(i)-1)) == 1
            if strcmp(outSentence(apostIndex(i)-1:apostIndex(i)+6),'d''accord') == 0 && strcmp(outSentence(apostIndex(i)-1:apostIndex(i)+5),'d''abord') == 0 && strcmp(outSentence(apostIndex(i)-1:apostIndex(i)+8),'d''ailleurs')== 0 && strcmp(outSentence(apostIndex(i)-1:apostIndex(i)+8),'d''habitude') == 0
                %needs to be seperated
                outSentence = [outSentence(1:apostIndex(i)) ' ' outSentence(apostIndex(i)+1:end)];
                if length(apostIndex) > i 
                    apostIndex = apostIndex + 1;
                    
                end
            end
        end
        %everything except d
        if strcmp('d', outSentence(apostIndex(i)-1)) == 0 && strcmp('l', outSentence(apostIndex(i)-1)) == 0 && strcmp('qu', outSentence(apostIndex(i)-2:apostIndex(i)-1)) == 0
            outSentence = [outSentence(1:apostIndex(i)) ' ' outSentence(apostIndex(i)+1:end)];
            if length(apostIndex) > i
                    apostIndex = apostIndex + 1;
            end
        end
    end
    
    outSentence = regexprep( outSentence, '\s+', ' ');

  end

  % change unpleasant characters to codes that can be keys in dictionaries
  outSentence = convertSymbols( outSentence );
  

