function build_wmc_structure(stat_sub, run)

if ~isdeployed
	addpath(genpath('/N/u/brlife/git/vistasoft'));
	addpath(genpath('/N/u/brlife/git/encode'))
	addpath(genpath('/N/u/brlife/git/jsonlab'))
	addpath(genpath('/N/u/kitchell/Karst/Applications/mba'))
	addpath(genpath('/N/soft/mason/SPM/spm8'))
	addpath(genpath('/N/dc2/projects/lifebid/code/kitchell/wma'))
end

%convert tck to fg
fid = fopen('tract_name_list.txt');
tline = fgetl(fid);

while ischar(tline)
    disp(tline);
    tck_filename = strcat('tracts_tck/',stat_sub,'_',tline,'_tract_',run,'.tck');
    fg_classified = dtiImportFibersMrtrix(tck_filename, 1);
    fgWrite(fg_classified, tline, 'mat');
    tline = fgetl(fid);
end

fclose(fid);

%merge fg structures
fid = fopen('tract_name_list.txt');
tline = fgetl(fid);
load(tline);
fg_class=fg;

while ischar(tline)
    disp(tline);
    load(tline);
    new_name = strrep(tline,'_',' ');
    fg.name = new_name;
    fg_class = [fg_class, fg];
    tline = fgetl(fid);
end

fgWrite(fg_class(2:end), 'fg_output', 'mat');
fclose(fid);

s = load('fg_output.mat');
fg_classified = s.fg;

names = {};
for i=1:length(s.fg)
names{i} = s.fg(i).name;
end

classification = [];
b = load('index.mat');
classification.index = b.idx;
classification.names = names;

save('output', 'classification', 'fg_classified');

tracts = fg2Array(fg_classified);

mkdir('tracts');

% Make colors for the tracts
%cm = parula(length(tracts));
cm = distinguishable_colors(length(tracts));
for it = 1:length(tracts)
   tract.name = strrep(tracts(it).name, '_', ' ');
   tract.name = sprintf('Tract %s', tract.name); %trick for visualization
   all_tracts(it).name = strrep(tracts(it).name, '_', ' ');
   all_tracts(it).name = sprintf('Tract %s', all_tracts(it).name); %trick for visualization
   all_tracts(it).color = cm(it,:);
   tract.color  = cm(it,:);

   %tract.coords = tracts(it).fibers;
   %pick randomly up to 1000 fibers (pick all if there are less than 1000)
   fiber_count = min(1000, numel(tracts(it).fibers));
   tract.coords = tracts(it).fibers(randperm(fiber_count)); 
   
   savejson('', tract, fullfile('tracts',sprintf('%i.json',it)));
   all_tracts(it).filename = sprintf('%i.json',it);
   clear tract
end

savejson('', all_tracts, fullfile('tracts/tracts.json'));


% saving text file with number of fibers per tracts
tract_info = cell(length(fg_classified), 2);

possible_error = 0;
for i = 1:length(fg_classified)
    tract_info{i,1} = fg_classified(i).name;
    tract_info{i,2} = length(fg_classified(i).fibers);
    if length(fg_classified(i).fibers) < 20
        possible_error=1;
    end
end

if possible_error==1
    results.quality_check = 'ERROR: Some tracts have less than 20 streamlines. Check quality of data!';
else
    results.quality_check = 'Data should be fine, but please view to double check';
end
savejson('', results, 'product.json');


T = cell2table(tract_info);
T.Properties.VariableNames = {'Tracts', 'FiberCount'};

writetable(T,'output_fibercounts.txt')


exit;
end
