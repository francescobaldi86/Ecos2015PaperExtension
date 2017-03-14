% Plotting for presentation

% %% Histogram propulsive power
% propulsive_power = energy.demand.propulsion / 1000 ;
% propulsive_power(propulsive_power < 0.100) = [] ; %Eliminating low power
% propulsive_power(propulsive_power > MCR_ME * 4 * 0.95 * 1e-3) = [] ; % Eliminating too high power
% figure
% histogram(propulsive_power,20,'Normalization','probability')
% xlabel('Power [MW]')
% ylabel('Frequency of occurrance')
% title('Propulsive power demand distribution')
% 
% 
% %% Histogram auxiliary power
% figure
% auxiliary_power = energy.demand.auxiliary_power / 1000 ;
% auxiliary_power(auxiliary_power < 0.100) = [] ; %Eliminating low power
% auxiliary_power(auxiliary_power > MCR_AE * 4 * 0.95 * 1e-3) = [] ; % Eliminating too high power
% histogram(auxiliary_power,20,'Normalization','probability')
% xlabel('Power [MW]')
% ylabel('Frequency of occurrance')
% title('Auxiliary power demand distribution')
% 
% 
% %% Histogram heat power
% figure
% heat_power = energy.demand.total_heat / 1000 ;
% heat_power(heat_power < 0.100) = [] ; %Eliminating low power
% histogram(heat_power,20,'Normalization','probability')
% xlabel('Power [MW]')
% ylabel('Frequency of occurrance')
% title('Heat demand distribution')
% 
% %% Plot head demand
% figure
% time = linspace(datenum('02-01-2014'),datenum('12-17-2014'),24*4*(28+31+30+31+30+31+31+30+31+30+16)) ;
% time(end) = [] ;
% [AX,H1,H2] = plotyy(time,heat_power,time,T_atm) ;
% set(get(AX(1),'Ylabel'),'String','Heat demand [MW]') 
% set(get(AX(2),'Ylabel'),'String','Air temperatyre [K]')
% set(H1,'LineWidth',1.5)
% set(H2,'LineStyle',':')
% datetick('x','mmm','keeplimits')
% xlabel('Time')
% ylabel('Power [MW]')
% legend('Heat demand','Air temperature')



%% Plot aux power demand vs temperature
figure
auxiliary_power = energy.demand.auxiliary_power / 1000 ;
[AX,H1,H2] = plotyy(time,auxiliary_power,time,T_atm) ;
set(get(AX(1),'Ylabel'),'String','Heat demand [MW]') 
set(get(AX(2),'Ylabel'),'String','Air temperatyre [K]')
set(H2,'LineStyle',':')
set(H2,'LineWidth',1.4)
datetick('x','mmm','keeplimits')
xlabel('Time')
ylabel('Power [MW]')
legend('Heat demand','Air temperature')