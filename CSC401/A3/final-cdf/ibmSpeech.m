function ibmSpeech()
speechToText()

function speechToText()
addpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));
dir_name = '/u/cs401/speechdata/Testing/';

directory = dir(dir_name);

flacs = {};

for i = 1:length(directory)
    filePath = [dir_name directory(i).name];
    flac_file = findstr('.flac', filePath);
    
    if isempty(flac_file) == 0
        flacs = [flacs, filePath];
    end
end

% sort_nat taken from http://www.mathworks.com/matlabcentral/fileexchange/10959-sort-nat--natural-order-sort
% (c) Douglas Schwarz, 03 May 2006

flacs = sort_nat(flacs);

username = '"a711ca46-290f-4bcc-ba26-3fbd4f71fd7c"';
password = '"Sz58pNM8WyYd"';

for i=1:length(flacs)
    [status, result] = unix(['env LD_LIBRARY_PATH="" curl -u ' username ':' password ' -X POST --header "Content-Type: audio/flac" --header "Transfer-Encoding: chunked" --data-binary @' flacs{i} ' "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?continuous=true"']);
    ref_index = findstr('transcript', result);
    if isempty(ref_index) == 0
        start = ref_index + 14;
        finish = findstr('}', result) - 15;
        ref = result(start:finish);
    end
    
    fileId = fopen('fromIbm.txt', 'a');
    fprintf(fileId, ['0 0 ' ref '\n']);
    fclose(fileId);
    
end
rmpath(genpath('/u/cs401/A3_ASR/code/FullBNT-1.0.7/'));
Levenshtein('fromIbm.txt', '/u/cs401/speechdata/Testing/');
