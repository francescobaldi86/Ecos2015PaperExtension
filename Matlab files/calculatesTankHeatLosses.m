function heat_loss_coefficient = calculatesTankHeatLosses(tank_id , folder_work , varargin)

load(char([folder_work 'tank_data.mat'])) ;

for i = 1 : length(TANK_NAMES)
    if strcmp(tank_id,char(TANK_NAMES(i))) == 1
        breadth = TANK_BREADTHS(i) ;
        width = TANK_BREADTHS(i) ;
        height = TANK_BREADTHS(i) ;
    end
end

% If there is the last argument, that is the volume filling in the tank and
% therefore represents the case in which we are actually telling that we
% include that in the calculation
if nargin == 4
    fluid_volume = varargin(1) ;
    height = fluid_volume / (breadth * width) ;
end

area = 2 * (breadth * width + breadth * height + width * height) ;

heat_loss_coefficient = area * TANK_LAMBDA / TANK_DELTA ;