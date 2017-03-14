% Script calculating the heat unbalance

time = (0:1:length(energy.demand.fuel_tanks)) / 4 ;
interval = 10100:1:10200 ;


for i = 1 : 4
    temp_Qwhr(:,1) = sum(ME_mfr_eg.(char(['ME' num2str(i)])) .* CP_EG .* (ME_T_eg.(char(['ME' num2str(i)]))(:,2) - 160),2) ;  
    temp_Qwhr(:,2) = sum(AE_mfr_eg.(char(['AE' num2str(i)])) .* CP_EG .* (AE_T_eg.(char(['AE' num2str(i)]))(:,2) - 160),2) ;
end

waste_heat_available_eg = sum(temp_Qwhr,2) ;
waste_heat_available_ht = sum(energy.ME.ht,2) + sum(energy.AE.ht,2) ;
waste_heat_available_tot = waste_heat_available_eg + waste_heat_available_ht ;



figure
% plot(...
%     time(interval),energy.demand.total_heat(interval),'r-',...
%     time(interval),waste_heat_available_eg(interval),'k--',...
%     time(interval),waste_heat_available_ht(interval),'k:',...
%     time(interval),waste_heat_available_tot(interval),'k-',...
%     'LineWidth',2)

hold on
area_demand = area(time(interval),energy.demand.total_heat(interval),'FaceColor','red','EdgeColor','Red') ;
area_tot = area(time(interval),waste_heat_available_tot(interval),'FaceColor','green') ;
patch_area_tot = get(area_tot,'children');
alpha(patch_area_tot,'clear')
plot_eg = plot(time(interval),waste_heat_available_eg(interval),'k:') ;
plot_ht = plot(time(interval),waste_heat_available_ht(interval),'k--') ;
legend('Thermal Energy Demand','Waste energy, total','Waste energy, exhaust','Waste Energy, HT water')
plot_demand = plot(time(interval),energy.demand.total_heat(interval),'r:','LineWidth',0.1) ;
xlabel('Time [h]') 
ylabel('Power [kW]')

