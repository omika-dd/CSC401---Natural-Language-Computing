function evalAlign()
%
% evalAlign
%
%  This is simply the script (not the function) that you use to perform your evaluations in 
%  Task 5. 

% some of your definitions
    trainDir     = '/u/cs401/A2_SMT/data/Hansard/Training/';
    testDir      = '/u/cs401/A2_SMT/data/Hansard/Testing/';
    fn_LME       = 'hansard_train_english.mat';
    fn_LMF       = 'hansard_train_french.mat';
    lm_type      = '';
    delta        = 0;
    vocabSize    = 0; 
    numSentences = 1000;
    maxIter = 10;

    outputFile = fopen('Task5Output.txt', 'w');
    % Train your language models. This is task 2 which makes use of task 1
    %LME = lm_train( trainDir, 'e', fn_LME );
    %LMF = lm_train( trainDir, 'f', fn_LMF );
    LME = load(fn_LME, '-mat', 'LM');

    % Train your alignment model of French, given English 
    %AMFE1 = align_ibm1( trainDir, numSentences, maxIter, 'AMFE1.mat' );
    %AMFE10 = align_ibm1( trainDir, 10000, maxIter, 'AMFE10.mat' );
    %AMFE15 = align_ibm1( trainDir, 15000, maxIter, 'AMFE15.mat' );
    %AMFE30 = align_ibm1( trainDir, 30000, maxIter, 'AMFE30.mat' );
    
    AMFE1 = load('am.mat', '-mat', 'AM');
    AMFE10 = load('AMFE10.mat', '-mat', 'AM');
    AMFE15 = load('AMFE15.mat', '-mat', 'AM');
    AMFE30 = load('AMFE30.mat', '-mat', 'AM');
    
    username = '"f6406116-4e3a-4c4f-8567-3c6135df6727"';
    password = '"VponljlkdNOb"';

    % TODO: a bit more work to grab the English and French sentences. 
    %       You can probably reuse your previous code for this  
    frenchSentences = textread('/u/cs401/A2_SMT/data/Hansard/Testing/Task5.f', '%s','delimiter','\n');
    engSentences = textread('/u/cs401/A2_SMT/data/Hansard/Testing/Task5.e', '%s','delimiter','\n');
    googleSentences = textread('/u/cs401/A2_SMT/data/Hansard/Testing/Task5.google.e', '%s','delimiter','\n');

    fprintf(outputFile, 'Task 5 Report\n');

    for l=1:length(frenchSentences)
        fre =  preprocess(frenchSentences{l}, 'f');
        eng = preprocess(engSentences{l}, 'e');
        goog = preprocess(googleSentences{l}, 'e');

        % add BlueMix code here 
        
        [status, result] = unix(['curl -u ' username ':' password ' -X POST -F "text=' frenchSentences{l} '" -F "source=fr" -F "target=en" "https://gateway.watsonplatform.net/language-translation/api/v2/translate"']);
        bluemix = preprocess(result, 'e');
        
        fprintf(outputFile, 'Sentence Number %d', l);
        fprintf(outputFile, '\nHansard French sentence: %s\n', fre);
        fprintf(outputFile, 'Hansard English sentence: %s\n', eng);
        fprintf(outputFile, 'Google Translate English sentence: %s\n', goog);
        fprintf(outputFile, 'IBM BlueMix English sentence: %s\n', bluemix);

        % Decode the test sentence 'fre'
        eng1 = decode( fre, LME.LM, AMFE1.AM, lm_type, delta, vocabSize );
        
        fprintf(outputFile, '\n\nAlignment Model Trained on %dk Sentences:\n', 1);
        res = convert_to_string(eng1);
        fprintf(outputFile, 'Result: %s\n', res);
        for i=1:3
            bleu = compute_bleu(eng1, eng, goog, bluemix, i);
            fprintf(outputFile, 'BLEU %d: %f\n',i, bleu); 
        end
        eng10 = decode( fre, LME.LM, AMFE10.AM, lm_type, delta, vocabSize );
        fprintf(outputFile, '\nAlignment Model Trained on %dk Sentences:\n', 10);
        res = convert_to_string(eng10);
        fprintf(outputFile, 'Result: %s\n', res);
        for i=1:3
            bleu = compute_bleu(eng10, eng, goog, bluemix, i);
            fprintf(outputFile, 'BLEU %d: %f\n',i, bleu); 
        end
        eng15 = decode( fre, LME.LM, AMFE15.AM, lm_type, delta, vocabSize );
        fprintf(outputFile, '\nAlignment Model Trained on %dk Sentences:\n', 15);
        res = convert_to_string(eng15);
        fprintf(outputFile, 'Result: %s\n', res);
        for i=1:3
            bleu = compute_bleu(eng15, eng, goog, bluemix, i);
            fprintf(outputFile, 'BLEU %d: %f\n',i, bleu); 
        end
        eng30 = decode( fre, LME.LM, AMFE30.AM, lm_type, delta, vocabSize );
        fprintf(outputFile, '\nAlignment Model Trained on %dk Sentences:\n', 30);
        res = convert_to_string(eng30);
        fprintf(outputFile, 'Result: %s\n', res);
        for i=1:3
            bleu = compute_bleu(eng30, eng, goog, bluemix, i);
            fprintf(outputFile, 'BLEU %d: %f\n',i, bleu); 
        end
        fprintf(outputFile, '\n\n');
    end
    fclose(outputFile);
end 

function bleu = compute_bleu(candidate, hansard, google, bluemix, n)
    %create reference bigrams and trigrams 
    refs = {hansard, google, bluemix};
    reference_grams = struct();
    
    for i = 1:length(refs)
        ref = refs{i};
        ref_split = strsplit(' ', ref);

        for j = 3:length(ref_split)
            first = ref_split{j-2};
            second = ref_split{j-1};
            
            third = ref_split{j};
            if (j == length(ref_split))
                reference_grams.(second).(third) = 1;
                reference_grams.(third) = 1;
            end
            reference_grams.(first).(second).(third) = 1; %covers 
        end
        
    end
    
    
    % calculate unigrams and bigram precisions
    % num = number of words in candidate (length candidate) (if n = 1)
    % c = number of words in candidate that are in at least one reference
    % p1 = c/num
    c1 = 0;
    c2 = 0;
    c3 = 0;

    candidate_split = candidate;%strsplit(' ', candidate);
    num = length(candidate_split);
    
    for j = 3:num
        first = candidate_split{j-2};
        second = candidate_split{j-1};
        third = candidate_split{j};
        if (j == num)
            if isfield(reference_grams, second)
                c1 = c1 + 1;
                if isfield(reference_grams.(second), third)
                    c2 = c2 + 1;
                end
            end
            if isfield(reference_grams, third)
                c1 = c1 + 1;
            end 
        end
        if isfield(reference_grams, first)
            c1 = c1 + 1;
            if isfield(reference_grams.(first), second)
                c2 = c2 + 1;
                if isfield(reference_grams.(first).(second), third)
                    c3 = c3 + 1;
                end
            end
        end
    end 
            
    p1 = c1/num;
    if n >= 2
        p2 = c2/(num-1);
        if n >= 3
            p3 = c3/(num-2);
        end
    end
    
    % Brevity
    % compare absolute differences of lengths of references and candidates
    % r1 = , r2 = , r3 =
    % c = 
    len_r1 = length(strsplit(' ', hansard));
    len_r2 = length(strsplit(' ', google));
    len_r3 = length(strsplit(' ', bluemix));
    lens = [len_r1 len_r2 len_r3];
    
    diff1 = abs(num - len_r1);
    diff2 = abs(num - len_r2);
    diff3 = abs(num - len_r3);
    
    diffs = [diff1 diff2 diff3];
    [M, I] = min(diffs(:));
    
    similar = lens(I);
    
    % for the smallest difference, calculate brevity
    % brevity = ref_length/candidate_length
    brevity = similar/num;
    
    % multiply precision by the (0..1) brevity penalty
    % if brevity < 1, bp = 1 else, bp = e^1-brevity
    if brevity < 1
        bp = 1;
    else 
        bp = exp(1-brevity);
    end 
    
    if n == 1
        bleu = bp * p1.^(1/n);
    elseif n == 2
        bleu = bp * (p1*p2).^(1/n);
    else 
        bleu = bp * (p1*p2*p3).^(1/n);
    end 
    
end 

function str = convert_to_string(cell_array)
    cell_arr_copy = cell_array;
    cell_arr_copy(2, :) = {' '};
    cell_arr_copy{2, end} = '';
    str = [cell_arr_copy{:}];
end