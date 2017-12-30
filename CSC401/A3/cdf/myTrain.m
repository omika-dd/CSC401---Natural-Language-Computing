function [HMM, LL] = myTrain(M, S, T, D, output)
% [HMM, LL] = myTrain(M, S, T, D, output)
%  Initialize and train continuous hidden Markov models for each phoneme
%  in the data set.
%
%  Note: Each model is trained on all data of a specific phoneme across all
%  speakers, so these models will be speaker-independent.
%
%  inputs: (used for 3.2 experimentation)
%          M: # mixtures
%          S: # states
%          T: # folders in training data to use
%          D: # dimensions
%          output: name of trained hmm output file
%
%  outputs:
%          [HMM, LL]          : list of trained HMM's with log likelihoods

addpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));

directory = '/u/cs401/speechdata/Training/';

folder = dir(directory);
folder = folder(4:end);
dimensions = 14;
% dimensions = D; used for 3.2 experimentation
% mixtures = M;
% states = S;
% training = T;

phoneme = struct();

phns = {};      % phns holds all the phn file paths
mfccs = {};     % mfccs holds all the mfcc file paths

for k = 1:length(folder)%training
    % display(folder(k).name)
    subfoldername = [directory folder(k).name];
    subfolders = dir(subfoldername);
    for j = 1:length(subfolders)
        filePath = [subfoldername '/' subfolders(j).name];
        extensionPHN = findstr('.phn', filePath);
        extensionMFCC = findstr('.mfcc', filePath);
        if isempty(extensionPHN) == 0
            phns = [phns, filePath];
        end 
        if isempty(extensionMFCC) == 0
            mfccs = [mfccs, filePath];
        end 
    end 
end

phnread = readFile(phns);
mfccread = readFile(mfccs);

% accumulate data from file into cell array of matrices formatted per file

phnMatrix = createMatrix(phnread, 3);
% display(phnMatrix);
% {41x3 cell}    {33x3 cell}    {56x3 cell}

mfccMatrix = createMatrix(mfccread, dimensions);
% display(mfccMatrix);
% {408x14 cell}    {319x14 cell}    {451x14 cell}

for i = 1:length(phnMatrix) % level: phn file
    for j = 1:length(phnMatrix{i}) % level: phn file line (phoneme)
        currentRow = phnMatrix{i}(j,:);
        startIndex = uint32(round(str2double(currentRow(1))/128)) + 1;
        endIndex = uint32(round((str2double(currentRow(2)))/128));
        endIndex = min(endIndex, length(mfccMatrix{i}));

        correspondingMFCCMatrix = str2double(mfccMatrix{i}(startIndex:endIndex, :));

        phone = currentRow(3);
        phone = phone{:};
        
        if strcmp(phone, 'h#')
            phone = 'sil';
        end
        
        if ~isfield(phoneme, phone)
            phoneme.(phone) = cell(0);
        end
        
        phoneme.(phone){length(phoneme.(phone)) + 1} = correspondingMFCCMatrix';
    end 
end

list_phonemes = fields(phoneme);
for i = 1:length(list_phonemes)
    current = list_phonemes{i};
    data = phoneme.(current);
    
    HMM = initHMM(data);
    [HMM, LL] = trainHMM(HMM, data, 7);
    save(['./hmm/', current], 'HMM', '-mat');
    
    % save(['./hmm-' output '/', current], 'HMM', '-mat');
end

rmpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));

return 

function fileRead = readFile(cell_array)
fileRead = {};
for i = 1:length(cell_array)
    fileId = fopen(cell_array{i}, 'r');
    fileRead = [fileRead, textscan(fileId, '%s')];
    fclose(fileId);
end 

function m = createMatrix(file_read, skip_by)
m = {};

for i = 1:length(file_read)
    single = {};
    for j = 1:skip_by:length(file_read{i})
        toAdd = {};
        for k = 1:skip_by
           toAdd = [toAdd, file_read{i}{j+(k-1)}];
        end 
        single = [single; toAdd];
    end
    m{i} = single;
end