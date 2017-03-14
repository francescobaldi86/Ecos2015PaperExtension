%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Calculating ship operational mode

% OM = 0 --> Not assigned
% OM = 1 --> Port stay
% OM = 2 --> Maneuvering
% OM = 3 --> Seagoing (low speed)
% OM = 4 --> Seagoing (high speed)
OM = zeros(n_data,1) ;

%% Assigning power to blower or to the rest of the ship
% If the derivate of the auxiliary power is higher than a given value, it
% means that the sharp increase in aux power is related to the use of
% thrusters
P_thruster = zeros(n_data,1) ;
P_aux_no_thruster = zeros(n_data,1) ;
P_aux_der = zeros(n_data,1) ;
der_P_aux = zeros(n_data,1) ;
for i = 2 : n_data
    der_P_aux(i) = P_aux(i) - P_aux(i-1) ;
    if der_P_aux(i) > 130 
        P_aux_no_thruster(i) = P_aux_no_thruster(i-1) ;
        P_thruster(i) = P_aux(i) - P_aux_no_thruster(i) ;
        OM(i) = 2 ;
    elseif der_P_aux(i) < -130
        P_aux_no_thruster(i) = P_aux(i) ;
        if der_P_aux(i-1) < -130
            P_aux_no_thruster(i-1) = P_aux_no_thruster(i-2) ;
            P_thruster(i-1) = P_aux(i-1) - P_aux_no_thruster(i-1) ;
        end
    elseif P_thruster(i-1) > 0
        P_aux_no_thruster(i) = P_aux_no_thruster(i-1) ;
        P_thruster(i) = P_aux(i) - P_aux_no_thruster(i) ;
        OM(i) = 2 ;
    else
        P_aux_no_thruster(i) = P_aux(i) ;
    end
end
%% Defining the operational mode
% If the blower is on, the ship is maneuvering
% If the speed is below 2 knots, the ship is in port
% If the speed is above 2 knots, the ship is at sea
for i = 1 : n_data
    if OM(i) ~= 2
        if ship_speed(i) < 2 
            OM(i) = 1 ;
        elseif ship_speed(i) < 15
            OM(i) = 3 ;
        else
            OM(i) = 4 ;
        end
    end
end

%% Checking on/off situation of all engines
for i = 1 : 4
    ME_on(:,i) = ME_pca(:,i) > 1.1 ;
    AE_on(:,i) = AE_PowerEl(:,i) > 0.05 * MCR_AE ;
end
ME_on(:,5) = sum(ME_on,2) > 0 ; % Equal to 1 if at least one engine is on
AE_on(:,5) = sum(AE_on,2) > 0 ; % Equal to 1 if at least one engine is on
