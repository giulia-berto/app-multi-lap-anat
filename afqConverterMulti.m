function out = afqConverterMulti(afq_filename, ref_src_filename)

if ~isdeployed
	addpath(genpath('/N/u/brlife/git/vistasoft'));
	addpath(genpath('/N/u/brlife/git/jsonlab'));
	addpath(genpath('/N/u/brlife/git/o3d-code'));
end

config = loadjson('config.json');
load(fullfile(char(afq_filename)));
ref_src = fullfile(char(ref_src_filename));

%convert afq to trk
disp('Converting afq to .trk');

%sub1
fid=fopen('tract_name_list.txt', 'w');

if (config.tract1 > 0)
    for tract = [config.tract1, config.tract2, config.tract3, config.tract4, config.tract5, config.tract6, config.tract7, config.tract8]
        if (tract > 0)
            tract_name=strrep(fg_classified(tract).name,' ','_');
            write_fg_to_trk_shift(fg_classified(tract),ref_src,sprintf('%s_tract.trk',tract_name));
            fprintf(fid, [tract_name, '\n']);
        end    
    end    
else
    for tract=1:length(fg_classified)
        tract_name=strrep(fg_classified(tract).name,' ','_');
        write_fg_to_trk_shift(fg_classified(tract),ref_src,sprintf('%s_tract.trk',tract_name));
        fprintf(fid, [tract_name, '\n']);  
    end 
end

fclose(fid);

exit;
end
