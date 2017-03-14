% BirkaEA_statistical_analysis
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% STATISTICAL ANALYSIS OF THE ENERGY AND EXERGY FLOWS %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% This script analyses somehow statistically the energy and exergy flows on
% board. 
%
% The analysis is based on the following categorisation based on
% operations:
% - High speed sailing (v_ship > v_ref)
% - Low speed sailing (v_ship <= v_ref)
% - Manoeuvring 
% - Port Stay
%
% For each of them, the following statistics are provided:
% - Average
% - Quartiles (25%-75%)
% - 5-95% Percentiles
%

%% Initial assignment of the new structures
energy_HSS = energy ; exergy_HSS = exergy ;
energy_LSS = energy ; exergy_LSS = exergy ;
energy_MAN = energy ; exergy_MAN = exergy ;
energy_POR = energy ; exergy_POR = exergy ;


%% Selecting the flows
% High speed sailing
applied_function = @(x) (x(OM==4,:)) ; 
    energy_HSS = structfunL2(energy_HSS,applied_function) ; 
    exergy_HSS = structfunL2(exergy_HSS,applied_function) ;
% Low speed sailing
applied_function = @(x) (x(OM==3,:)) ; 
    energy_LSS = structfunL2(energy_LSS,applied_function) ; 
    exergy_LSS = structfunL2(exergy_LSS,applied_function) ;
% Maneuvering
applied_function = @(x) (x(OM==2,:)) ; 
    energy_MAN = structfunL2(energy_MAN,applied_function) ;
    exergy_MAN = structfunL2(exergy_MAN,applied_function) ;
% Port stay
applied_function = @(x) (x(OM==1,:)) ; 
    energy_POR = structfunL2(energy_POR,applied_function) ;
    exergy_POR = structfunL2(exergy_POR,applied_function) ;

%% Assigning average values
applied_function = @(x) (mean(x,1)) ;
% Energy
energy_ave_HSS = structfunL2(energy_HSS,applied_function) ;
energy_ave_LSS = structfunL2(energy_LSS,applied_function) ;
energy_ave_MAN = structfunL2(energy_MAN,applied_function) ;
energy_ave_POR = structfunL2(energy_POR,applied_function) ;
% Exergy
exergy_ave_HSS = structfunL2(exergy_HSS,applied_function) ;
exergy_ave_LSS = structfunL2(exergy_LSS,applied_function) ;
exergy_ave_MAN = structfunL2(exergy_MAN,applied_function) ;
exergy_ave_POR = structfunL2(exergy_POR,applied_function) ;

%% Assigning 25 percentile values
applied_function = @(x) (prctile(x,25)) ;
% Energy
energy_25prctile_HSS = structfunL2(energy_HSS,applied_function) ;
energy_25prctile_LSS = structfunL2(energy_LSS,applied_function) ;
energy_25prctile_MAN = structfunL2(energy_MAN,applied_function) ;
energy_25prctile_POR = structfunL2(energy_POR,applied_function) ;
% Exergy
exergy_25prctile_HSS = structfunL2(exergy_HSS,applied_function) ;
exergy_25prctile_LSS = structfunL2(exergy_LSS,applied_function) ;
exergy_25prctile_MAN = structfunL2(exergy_MAN,applied_function) ;
exergy_25prctile_POR = structfunL2(exergy_POR,applied_function) ;
%% Assigning 75 percentile values
applied_function = @(x) (prctile(x,75)) ;
% Energy
energy_75prctile_HSS = structfunL2(energy_HSS,applied_function) ;
energy_75prctile_LSS = structfunL2(energy_LSS,applied_function) ;
energy_75prctile_MAN = structfunL2(energy_MAN,applied_function) ;
energy_75prctile_POR = structfunL2(energy_POR,applied_function) ;
% Exergy
exergy_75prctile_HSS = structfunL2(exergy_HSS,applied_function) ;
exergy_75prctile_LSS = structfunL2(exergy_LSS,applied_function) ;
exergy_75prctile_MAN = structfunL2(exergy_MAN,applied_function) ;
exergy_75prctile_POR = structfunL2(exergy_POR,applied_function) ;


aaa = 0 ;