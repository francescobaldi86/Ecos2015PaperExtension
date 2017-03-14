%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Power demand       %%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Propulsion power
            energy.demand.propulsion = sum(energy.ME.Power,2) ;
            energy.demand.auxiliary_power = sum(energy.AE.PowerEl,2) ;
            energy.demand.thrusters = P_thruster ;
            exergy.demand.propulsion = sum(energy.ME.Power,2) ;
            exergy.demand.auxiliary_power = sum(energy.AE.PowerEl,2) ;
            exergy.demand.thrusters = P_thruster ;