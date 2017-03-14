%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% HEAT DEMAND - TOP DOWN - MINIMUM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%
% This script calculates the heat demand on board using a Top Down
% approach. This means that it is based on measurements, more than on
% physical principles and on the knowledge of the functioning principles of
% the ship. 
%
% This is calculated for two boundary cases: the "minimum" and the "maximum", based on two different assumptions 
% - In the MINIMUM case, the main assumption is that the HT heat is only
% used when in port to its maximum. On the other hand, when sailing, it is
% not used at all.
%
% - In the MAXIMUM case it is assumed that the HT heat is always used first, so that 
% a specific fraction (i.e. 90%) of the available HT heat is used. 
%
% In both cases, it is for the moment assumed that the heat from the
% boilers is used only in port, uniformly during port stays.


%% Boilers
% I basically assign the boilers only to time spent in port. 
% The consumption from the boilers, in the TopDown approach, is the same in
% both cases
load(char([folder_main 'fuel_consumption_daily.mat'])) ;
for i = 1 : length(Daily_fuel_consumption) % the i index is 1 per day
    AB_running_hours(i) = sum(OM(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) == 1) ; % Amount of hours on the i-th day spent in port
    AB_Mfuel(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) = (OM(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) ==1) .* (Daily_fuel_consumption(i,2) + Daily_fuel_consumption(i,4)) / AB_running_hours(i) / 15 / 60 ;
    AB_heat(i) = (Daily_fuel_consumption(i,2) + Daily_fuel_consumption(i,4)) / AB_running_hours(i) / 15 / 60 * LHV * ETA_BOILER ;
        energy.Qdem.topDown_AB(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) = (OM(DAY_LIMIT(i) : DAY_LIMIT(i+1) , 1) ==1) * AB_heat(i) ;
end
%% HRSG
% Also this contribution is the same in all cases
energy.Qdem.topDown_hrsgME = sum(energy.ME.hrsg,2) ;
energy.Qdem.topDown_hrsgAE = sum(energy.AE.hrsg,2) ;
%% HTHR
energy.Qdem.topDown_hthrMin = sum(energy.AE.ht,2) * HTHR_UTILISATION_FACTOR .* (OM == 1) ; % The HTHR is only used in port
energy.Qdem.topDown_hthrMax = (sum(energy.AE.ht,2) + sum(energy.ME.ht,2)) * HTHR_UTILISATION_FACTOR ; % All the heat from the HT available is used whenever possible
energy.Qdem.topDown_hthrAve = (energy.Qdem.topDown_hthrMin + energy.Qdem.topDown_hthrMax) / 2 ; % Average

%% Total heat
energy.Qdem.topDown_totalMin = energy.Qdem.topDown_AB + energy.Qdem.topDown_hrsgME + energy.Qdem.topDown_hrsgAE + energy.Qdem.topDown_hthrMin ;
energy.Qdem.topDown_totalMax = energy.Qdem.topDown_AB + energy.Qdem.topDown_hrsgME + energy.Qdem.topDown_hrsgAE + energy.Qdem.topDown_hthrMax ;

            
            


