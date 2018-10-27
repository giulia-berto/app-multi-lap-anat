function out = afqConverter1()

if ~isdeployed
	addpath(genpath('/N/u/brlife/git/vistasoft'));
	addpath(genpath('/N/u/brlife/git/jsonlab'));
	addpath(genpath('/N/u/brlife/git/o3d-code'));
end

config = loadjson('config.json');
ref_src = fullfile(config.t1_static);

%convert afq to trk
disp('Converting afq to .trk');

%sub1
load(fullfile(config.true_segmentation));

if (config.tract1 > 0)
    for tract = [config.tract1, config.tract2, config.tract3, config.tract4]
        if (tract > 0)
            tract_name=strrep(fg_classified(tract).name,' ','_');
            write_fg_to_trk_shift(fg_classified(tract),ref_src,sprintf('%s_tract.trk',tract_name));
        end    
    end    
else
    for tract=1:20
        tract_name=strrep(fg_classified(tract).name,' ','_');
        write_fg_to_trk_shift(fg_classified(tract),ref_src,sprintf('%s_tract.trk',tract_name));
        fprintf(fid, [tract_name, '\n']);  
    end 
end

exit;
end


