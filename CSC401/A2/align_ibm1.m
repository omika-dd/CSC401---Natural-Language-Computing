function AM = align_ibm1(trainDir, numSentences, maxIter, fn_AM)
%
%  align_ibm1
% 
%  This function implements the training of the IBM-1 word alignment algorithm. 
%  We assume that we are implementing P(foreign|english)
%
%  INPUTS:
%
%       dataDir      : (directory name) The top-level directory containing 
%                                       data from which to train or decode
%                                       e.g., '/u/cs401/A2_SMT/data/Toy/'
%       numSentences : (integer) The maximum number of training sentences to
%                                consider. 
%       maxIter      : (integer) The maximum number of iterations of the EM 
%                                algorithm.
%       fn_AM        : (filename) the location to save the alignment model,
%                                 once trained.
%
%  OUTPUT:
%       AM           : (variable) a specialized alignment model structure
%
%
%  The file fn_AM must contain the data structure called 'AM', which is a 
%  structure of structures where AM.(english_word).(foreign_word) is the
%  computed expectation that foreign_word is produced by english_word
%
%       e.g., LM.house.maison = 0.5       % TODO
% 
% Template (c) 2011 Jackie C.K. Cheung and Frank Rudzicz
  
  global CSC401_A2_DEFNS
  
  AM = struct();
  
  % Read in the training data
  [eng, fre] = read_hansard(trainDir, numSentences);

  % Initialize AM uniformly 
  AM = initialize(eng, fre);

  % Iterate between E and M steps
  for iter=1:maxIter,
    AM = em_step(AM, eng, fre);
  end

  % Save the alignment model
  save( fn_AM, 'AM', '-mat'); 

  end





% --------------------------------------------------------------------------------
% 
%  Support functions
%
% --------------------------------------------------------------------------------

function [eng, fre] = read_hansard(mydir, numSentences)
%
% Read 'numSentences' parallel sentences from texts in the 'dir' directory.
%
% Important: Be sure to preprocess those texts!
%
% Remember that the i^th line in fubar.e corresponds to the i^th line in fubar.f
% You can decide what form variables 'eng' and 'fre' take, although it may be easiest
% if both 'eng' and 'fre' are cell-arrays of cell-arrays, where the i^th element of 
% 'eng', for example, is a cell-array of words that you can produce with
%      eng{i} = strsplit(' ', preprocess(english_sentence, 'e'));
%
%  eng = {};
%  fre = {};


 
  % TODO: your code goes here.
  eng = {};
  fre = {};
  %temporary cell-arrays to read into 
  engread = {};
  freread = {};
  
  %reading contents of mydir into engread and freread
  Files = dir(mydir);
  FileNames= {};
  
  for k = 1:length(Files)
      FileNames = [FileNames, Files(k).name];
      filePath = [mydir Files(k).name];
      %english files
      extensionE = findstr('.e', filePath);
      %french files
      extensionF = findstr('.f', filePath);
      
      if isempty(extensionE) == 0   %english
        fileId = fopen(filePath, 'r');
        engread = [engread, textscan(fileId, '%s', numSentences, 'Delimiter', '\n')];
        fclose(fileId);
      end
      
      if isempty(extensionF) == 0   %french
        fileId = fopen(filePath, 'r');
        freread = [freread textscan(fileId, '%s', numSentences, 'Delimiter', '\n')];
        fclose(fileId);
      end
  end
 
  %filling in the eng and fre arrays
  %Eng and fre are cell-arrays where each cell contains another cell-array of numSentences number of lines from
  %each file in myDir. For instance, if numSentences = 2 and there are two
  %files in myDir, then eng{1} contains a cell-array of the first two preprocessed, tokenized
  %sentences from file1 and eng{2} contains a cell-array of the first two sentences from
  %file2. 
  k = 1;
  total = length(engread)+ length(engread{1});
  while k < total + 1
    for j = 1:size(engread,2) 
      for i = 1:size(engread{j},1) 
          english_sentence = engread{j}{i};
          eng{k} =strsplit(' ', preprocess(english_sentence, 'e'));
          k = k + 1;
        end
      end
  end

        
  
  l = 1;
  totalLength = length(freread)+ length(freread{1});
  while l < totalLength + 1
    for j = 1:size(freread,2) %number of files 
        for i = 1:size(freread{j},1)
        french_sentence = freread{j}{i};
        fre{l} = strsplit(' ', preprocess(french_sentence, 'f'));
        l = l + 1;
        end
    end
  end
  
end



function AM = initialize(eng, fre)
%
% Initialize alignment model uniformly.
% Only set non-zero probabilities where word pairs appear in corresponding sentences.
%
    AM = {};% AM.(english_word).(foreign_word)
    % TODO: your code goes here
    
    
        for i = 1:length(eng) %i iterates over each sentence
            for j = 1:length(eng{i}) %each word
                for k = 1:length(fre{i})
                    AM.(eng{i}{j}).(fre{i}{k}) = 1/length(unique(fre{i}));
                        
                end
            end
        end
                            
                      
    %assigning proper probabilites                 
    for field = fieldnames(AM)'
        
        count = length(fieldnames(AM.(field{1})));
        for subfield = fieldnames(AM.(field{1}))'
                if strcmp(field,'SENTSTART') && strcmp(subfield,'SENTSTART')
                    AM.(field{1}).(subfield{1}) = 1;
                
                elseif strcmp(field,'SENTEND') && strcmp(subfield,'SENTEND')
                    AM.(field{1}).(subfield{1}) = 1;
                else
                    AM.(field{1}).(subfield{1}) = 1/count;
                end
        end 
    end
   
end
                   
                     
function new_array = unique_c(orig_array)
    index = 1; 
    while index < size(orig_array,1) 
        t = true(size(orig_array,1), 1); 
        for index2 = index:size(orig_array, 1) 
            if isequal(orig_array(index, :),orig_array(index2, :)) && index ~= index2 
                t(index2) = 0; 
            end 
        end 
        orig_array = orig_array(t, :); 
        index = index + 1; 
    end
    new_array = orig_array;
end

    
function t = em_step(t, eng, fre)
% 
% One step in the EM algorithm.
%
  
  % TODO: your code goes here
  tcount = struct();
  total = struct();
  
  for i=1:length(eng)
      french = fre{i};
      english = eng{i};
      unique_f = unique_c(french);
      for j=1:length(unique_f)
          fr = unique_f{j};
          denom_c = 0;
          unique_e = unique_c(english);
          for k=1:length(unique_e)
              denom_c = denom_c + t.(unique_e{k}).(fr) * sum(strcmp (french, fr));
          end
          for k=1:length(unique_e)
              en = unique_e{k};
              fCount = sum(strcmp (french, fr));
              eCount = sum(strcmp (english, en));
              count = t.(en).(fr) * fCount * eCount/denom_c;
              tot = t.(en).(fr) * fCount * eCount/denom_c;
              
              if isfield(tcount, en) == 0
                  tcount.(en) = struct();
              end
              if isfield(tcount.(en), fr) == 0
                  tcount.(en).(fr) = 0;
              end 
              tcount.(en).(fr) = tcount.(en).(fr) + count;

              if isfield(total, en) == 0
                  total.(en) = 0;
              end
              total.(en) = total.(en) + tot;
          end     
      end
  end
  total_domain = fieldnames(total);
  
  for i=1:length(total_domain)
      en = total_domain{i};
      
      tcount_domain = fieldnames(tcount.(en));
      for j=1:length(tcount_domain)
          fr = tcount_domain{j};
          t.(en).(fr) = tcount.(en).(fr)/total.(en);
      end
  end
      
end


