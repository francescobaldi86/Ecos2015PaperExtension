%%%%%%%%%%%%%%%%%%%%%%
%%% EARLY ELABORATIONS
%%%%%%%%%%%%%%%%%%%%%%

clear temp*

%% Some assumptions about storage tanks
% Settling tanks
T_fuel_tanks(:,5) = ones(n_data,1) * 85 + 273 ;
T_fuel_tanks(:,6) = ones(n_data,1) * 85 + 273 ;
% Storage tank
T_fuel_tanks(:,7) = ones(n_data,1) * 50 + 273 ;



%% Data filtering 
% Part 1 - Defining the limits (fixed or load-dependent) based on engine
% shop trials
x_load_me = [0.25 0.5 0.75 0.85 1] ;
% For the main engines
DATA_FILTERING_LIMITS.ORIGINAL.ME_Teg_aEng = polyfit(x_load_me,[520 465 470 473 523]+273,2) ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_Teg_aTC = polyfit(x_load_me,[469 288 326 315 346]+273,2) ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tht_bEng = [60 90] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tht_aEng_R = [65 100] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tlt_bEng = [25 50] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tfuel = [50 200] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tlo_bEng = [55 80] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tlo_aEng = [60 85] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.ME_pca = polyfit(x_load_me,[1.32 2.49 3.43 3.82 4.15],2) ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_Tca = [30 70] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_rpm = [100 , 510] ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_frp = [0 , 1] ;
DATA_FILTERING_LIMITS.ORIGINAL.ME_rpmTC = polyfit(x_load_me,[8333 16959 19363 20567 21635],2) ;
% For the auxiliary engines
x_load_ae = [0.25 0.5 0.75 1] ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Teg_aEng = polyfit(x_load_ae,[398 454 478 496]+273,2) ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Teg_aTC = polyfit(x_load_ae,[334 360 355 342]+273,2) ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tfuel = [50 200] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tlo_aEng = [60 85] + 273 ; 
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tht_bEng = [60 90] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tht_aJWC = [65 100] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tht_aCAC = [65 100] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tlt_bEng = [25 50] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tlt_aCAC = [30 60] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tlt_bLOC = [30 60] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_pca = polyfit(x_load_ae,[1.32 2.49 3.43 4.15]*0.8,2) ; % NOTE: same values as for the main engines. More margin should be given in this case
DATA_FILTERING_LIMITS.ORIGINAL.AE_Tca = [30 70] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_frp = [0 , 1] ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_rpm = [700 800] ;
DATA_FILTERING_LIMITS.ORIGINAL.AE_PowerEl = [0 2800] ;
% Other
DATA_FILTERING_LIMITS.ORIGINAL.T_fuel_tanks = [40 100] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_fuel_tanks_ref = [40 100] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_LTcooling = [20 60] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_HTcooling = [60 100] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.ship_speed = [0 25] ;
DATA_FILTERING_LIMITS.ORIGINAL.T_sea_water = [-1 30] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_hot_water = [10 120] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.p_steam_boiler = [4 7] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_atm = [-10 40] + 273 ;
DATA_FILTERING_LIMITS.ORIGINAL.T_ER = [20 40] + 273 ;

FILTERED_VARIABLES = fields(DATA_FILTERING_LIMITS.ORIGINAL) ;
DATA_FILTERING_LIMITS.USABLE = DATA_FILTERING_LIMITS.ORIGINAL ;

% Opening the log file
logfile_ID = fopen(char([folder_work filename_log_file]),'w') ;

% Part 2 - Setting expected limits for load-dependent measurements:
for idx = 1 : 4
        load_ME_temp = smoothCircularTransition(ME_POLY_PCA_2_LOAD(1,:),ME_POLY_PCA_2_LOAD(2,:),ME_POLY_PCA_2_LOAD(3,1),ME_pca(:,idx)-1,4) * 0.95 ;
        temp_ME_run = load_ME_temp > 0.05 ;
        temp1 = AE_PowerEl(:,idx) / AE_ETA_SG ; load_AE_temp = temp1 / MCR_AE ;
        temp_AE_run = load_AE_temp > 0.05 ;
    % For the main engines
    DATA_FILTERING_LIMITS.USABLE.ME_Teg_aEng = ones(n_data,1) * [-100 50] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.ME_Teg_aEng,load_ME_temp) * [1 1] ;
    DATA_FILTERING_LIMITS.USABLE.ME_Teg_aTC = ones(n_data,1) * [-100 50] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.ME_Teg_aTC,load_ME_temp) * [1 1] ;
    DATA_FILTERING_LIMITS.USABLE.ME_Teg_aHRSG = [(160+273)*ones(n_data,1) DATA_FILTERING_LIMITS.USABLE.ME_Teg_aTC(:,1)] ;
    DATA_FILTERING_LIMITS.USABLE.ME_pca = ones(n_data,1) * [-0.5 0.5] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.ME_pca,load_ME_temp) * [1 1] ;
    DATA_FILTERING_LIMITS.USABLE.ME_rpmTC = ones(n_data,1) * [-1000 1000] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.ME_rpmTC,load_ME_temp) * [1 1] ;
    % For the auxiliary engines
    DATA_FILTERING_LIMITS.USABLE.AE_Teg_aEng = ones(n_data,1) * [-50 50] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.AE_Teg_aEng,load_AE_temp) * [1 1] ;
    DATA_FILTERING_LIMITS.USABLE.AE_Teg_aTC = ones(n_data,1) * [-50 50] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.AE_Teg_aTC,load_AE_temp) * [1 1] ;
    DATA_FILTERING_LIMITS.USABLE.AE_Teg_aHRSG = [(160+273)*ones(n_data,1) DATA_FILTERING_LIMITS.USABLE.AE_Teg_aTC(:,1)] ;
    DATA_FILTERING_LIMITS.USABLE.AE_pca = ones(n_data,1) * [-0.5 0.5] + polyval(DATA_FILTERING_LIMITS.ORIGINAL.AE_pca,load_AE_temp) * [1 1] ;
    for idx1 = 1 : length(FILTERED_VARIABLES)
        temp0 = char(FILTERED_VARIABLES(idx1)) ;
        if strcmp(temp0(1:2),'ME') == 1 
            eval(char(['temp1 = ' , char(FILTERED_VARIABLES(idx1)) , '(:,idx) ;'])) ;
            temp2 = ((temp1 <  DATA_FILTERING_LIMITS.USABLE.(char(FILTERED_VARIABLES(idx1)))(:,1)) | (temp1 >  DATA_FILTERING_LIMITS.USABLE.(char(FILTERED_VARIABLES(idx1)))(:,2))) & (temp_ME_run) ; 
            fprintf(logfile_ID,'\n %g Data points out of %g eliminated based on the variable %s of ME%g',sum(temp2),n_data,char(FILTERED_VARIABLES(idx1)),idx) ;
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%
        elseif strcmp(temp0(1:2),'AE') == 1
            eval(char(['temp1 = ' , char(FILTERED_VARIABLES(idx1)) , '(:,idx) ;'])) ;
            temp2 = ((temp1 <  DATA_FILTERING_LIMITS.USABLE.(char(FILTERED_VARIABLES(idx1)))(:,1)) | (temp1 >  DATA_FILTERING_LIMITS.USABLE.(char(FILTERED_VARIABLES(idx1)))(:,2))) & (temp_AE_run) ; 
            fprintf(logfile_ID,'\n %g Data points out of %g eliminated based on the variable %s of AE%g',sum(temp2),n_data,char(FILTERED_VARIABLES(idx1)),idx) ;
        end
    end
    fprintf(logfile_ID,'\n') ;
end

fclose(logfile_ID) ;
% Other
aa = 0 ;


