function [SE IE DE LEV_DIST] =Levenshtein(hypothesis,annotation_dir)
% Input:
%	hypothesis: The path to file containing the the recognition hypotheses
%	annotation_dir: The path to directory containing the annotations
%			(Ex. the Testing dir containing all the *.txt files)
% Outputs:
%	SE: proportion of substitution errors over all the hypotheses
%	IE: proportion of insertion errors over all the hypotheses
%	DE: proportion of deletion errors over all the hypotheses
%	LEV_DIST: proportion of overall error in all hypotheses


reference_words = 0;
% SE = # substituted words / # reference words
SE = 0;

% IE = # inserted words / # reference words
IE = 0;

% DE = # deleted words / # reference words
DE = 0;

dir_ann = dir(annotation_dir);

fileId = fopen(hypothesis, 'r');
hypotheses = textscan(fileId, '%s', 'delimiter', '\n');
fclose(fileId);

hypotheses = hypotheses{1};
text_files = {};

for i=1:length(dir_ann)
    file_path = [annotation_dir dir_ann(i).name];
    txt_file = findstr('.txt', file_path);
    if isempty(txt_file) == 0 && strcmp('hypotheses.txt', dir_ann(i).name) == 0 && strcmp('TestingIDs1-15.txt', dir_ann(i).name) == 0
        text_files = [text_files, file_path];
    end
end

references = {};
for i = 1:length(text_files)
    fileId = fopen(text_files{i}, 'r');
    temp = textscan(fileId, '%s', 'delimiter', '\n');
    references = [references, temp{1}{1}];
    fclose(fileId);
end

for k=1:length(references)
    ref = lower(references{k});
    ref_split = regexp(ref, ' ', 'split');
    ref_split = ref_split(3:end);
    n = length(ref_split);
    reference_words = reference_words + n;
    
    [corresponding_line, rest] = strtok(text_files{k}, '_');
    [corresponding_line, rest] = strtok(rest(2:end), '.');
    index = str2num(corresponding_line);
    hyp = lower(hypotheses{index});
    hyp_split = regexp(hyp, ' ', 'split');
    hyp_split = hyp_split(3:end);
    m = length(hyp_split);
%    disp(['unkn_' corresponding_line ': ' hyp]);
    
    temp_n = n+1;
    temp_m = m+1;
    
    r = Inf(temp_n, temp_m);
    r(1,1) = 0;
    
    c = zeros(temp_n, temp_m);
    actions = zeros(1,4); % format: delete, insert, sub_differ/substitute, sub_match
    
    for i = 2:temp_n
        for j = 2:temp_m
            delete = r(i-1, j) + 1;
            insert = r(i, j-1) + 1;
            sub_differ = r(i-1,j-1) + 1;
            matches = ~strcmp(ref_split{i-1}, hyp_split{j-1});
            sub_match = r(i-1,j-1) + matches;
           
            [r(i,j), choice] = min([delete, insert, sub_differ, sub_match]);
            c(i,j) = choice;
        end
    end

    while (temp_n ~= 1) && (temp_m ~= 1)
        move = c(temp_n, temp_m);
        actions(move) = 1 + actions(move);
        x = move ~= 2;
        y = move ~= 1;
        temp_n = temp_n - x;
        temp_m = temp_m - y;
    end
    
    delete = actions(1);
    insert = actions(2);
    substitute = actions(3);
    
%   disp(['DE = ' num2str(delete) ' IE = ' num2str(insert) ' SE = ' num2str(substitute)]);
%    disp((delete + insert + substitute)/n);

    DE = DE + delete;
    IE = IE + insert;
    SE = SE + substitute;
end

%disp(['DE = ' num2str(DE) ' IE = ' num2str(IE) ' SE = ' num2str(SE)]);
LEV_DIST =  (SE + IE + DE)/reference_words;
%disp(['LEV_DIST = ' num2str(LEV_DIST)]);

