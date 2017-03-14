heat_available = energy.ME.ht(:,1) + energy.ME.ht(:,2) + energy.ME.ht(:,3) + energy.ME.ht(:,4) +...
    energy.ME.hrsg(:,1) + energy.ME.hrsg(:,2) + energy.ME.hrsg(:,3) + energy.ME.hrsg(:,4) + ...
    energy.AE.ht(:,1) + energy.AE.ht(:,2) + energy.AE.ht(:,3) + energy.AE.ht(:,4) +...
    energy.AE.hrsg(:,1) + energy.AE.hrsg(:,2) + energy.AE.hrsg(:,3) + energy.AE.hrsg(:,4) ;
heat_demand = energy.demand.total_heat2 ;

selection_for_heat_map = 0:250:10000 ;
heat_map = zeros(length(selection_for_heat_map)-1) ;
for idx1 = 1 : length(selection_for_heat_map)-1 
    for idx2 = 1 : length(selection_for_heat_map)-1
        heat_map(idx1,idx2) = sum((heat_demand<selection_for_heat_map(idx1+1)) & (heat_demand>=selection_for_heat_map(idx1)) & (heat_available<selection_for_heat_map(idx2+1)) & (heat_available>=selection_for_heat_map(idx2))) ;
    end
end
figure
plot(energy.demand.total_heat,heat_available,'bx')
xlabel('Heat demand [kW]') ; ylabel('Waste heat available [kW]') ;
HeatMap(heat_map,'RowLabels',selection_for_heat_map(2:end),'ColumnLabels',selection_for_heat_map(2:end),'Symmetric',false,'Colormap','redbluecmap')
        

