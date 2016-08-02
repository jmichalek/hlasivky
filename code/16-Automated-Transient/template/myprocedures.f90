FUNCTION vprofile(Model, n) RESULT(v)

  USE Types
  USE DefUtils
  IMPLICIT NONE
  TYPE(Model_t) :: Model
  INTEGER :: n
  real(KIND=dp)            :: v,y ! computed vars
  real(KIND=dp), PARAMETER :: deltay=0.0000_dp,ymax=TMPYMAX_dp,vmax=TMPVMAX_dp
  
  y = Model % Nodes % y(n) 
  ! elmer syntax to get the y coordinate from the considered node
  
IF (deltay<y .AND. y<ymax-deltay) THEN
  v=vmax*(y-deltay)*(ymax-deltay-y)/(ymax/2.0_dp-deltay)**2
ELSE
  v=0.0_dp
END IF

END FUNCTION vprofile
