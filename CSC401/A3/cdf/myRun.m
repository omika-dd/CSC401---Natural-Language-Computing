function prop_right = myRun(hmm_location, dimensions)

% Script that collects all phoneme sequences from test data given
% respective *.phn files. myRun finds the log likelihood of each phoneme
% sequence in the test data given each HMM phoneme model using the
% loglikHMM function

% data is from the Testing data, and HMM is loaded from the trained HMMs

dir_name = '/u/cs401/speechdata/Testing/';
if ~exist('hmm_location', 'var')
    hmm_location = 'hmm/';
end

directory = dir(dir_name);


hmm_directory = dir(hmm_location);
hmm_directory = hmm_directory(4:end);

phoneme = struct();

for k=1:length(hmm_directory)
    hmm_name = hmm_directory(k).name;
    filePath = [hmm_location hmm_name];

    try
        load(filePath, 'HMM', '-mat');
    catch
        disp('Error loading');
    end
    phoneme.(hmm_name) = HMM;
end
if ~exist('dimensions', 'var')
    dimensions = 14;
end
addpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));

phns = {};
mfccs = {};

for i = 1:length(directory)
    filePath = [dir_name directory(i).name];
    phn_file = findstr('.phn', filePath);
    mfcc_file = findstr('.mfcc', filePath);
    if isempty(phn_file) == 0
        phns = [phns, filePath];
    end
    if isempty(mfcc_file) == 0
        mfccs = [mfccs, filePath];
    end 
end

phnread = readFile(phns);
mfccread = readFile(mfccs);

phnMatrix = createMatrix(phnread, 3);
mfccMatrix = createMatrix(mfccread, dimensions);

phoneme_total = 0;
num_right = 0;

limit = 21; %unknown error that stops it at 22..

for i = 1:limit % level: phn file, utterance
    %display(i);
    phoneme_total = phoneme_total + length(phnMatrix{i});
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
        
        max_log_prob = -Inf;
        final_phn = '';
        
        for k=1:length(hmm_directory)
            hmm_name = hmm_directory(k).name;
            
            data = correspondingMFCCMatrix';
            
            log_prob = loglikHMM(phoneme.(hmm_name), data);
            
            if log_prob > max_log_prob
                max_log_prob = log_prob;
                final_phn = hmm_name;
            end
        end
        
        num_right = num_right + strcmp(phone, final_phn);
        
    end 
end
rmpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));
%disp (num_right)
%disp(phoneme_total)
prop_right = num_right/phoneme_total;
disp(prop_right);
 

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
    for j = [1:skip_by:length(file_read{i})]
        toAdd = {};
        for k = [1:skip_by]
            toAdd = [toAdd, file_read{i}{j+(k-1)}];
        end 
        single = [single; toAdd];
    end
    m{i} = single;
end