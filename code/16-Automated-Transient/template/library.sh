

# -----------------------------------
# Function fillIn()
# -----------------------------------

# Replaces TMPvarname with the value of $varname in a text file

fillIn() {
# $1 = varname
# $2 = filename

placeholder="TMP"$(awk '{print toupper($0)}' <<< "$1")

# echo placeholder $placeholder, value $value, var ${!1}

awk -v value="${!1}" -v placeholder="$placeholder" '
    {gsub(placeholder, value); print > "tmp" }' "$2"
mv tmp "$2"
echo "The variable $1 was written with the value ${!1}"
}

# -----------------------------------
# Function watchAndSync()
# -----------------------------------

# Watches for changes and copies result to a directory


watchAndSync() {
# we are in the start directory
while true; do 
  if ls "mesh/"*".vtu" 1> /dev/null 2>&1; then
    mv "mesh/case"*".vtu" "results" >> results/report.log 2>&1 
  fi
 sleep 5; 
done
}

# -----------------------------------
# Function watchAndSyncRemote()
# -----------------------------------

# Watches for changes in remote dir and copies result to a local directory


watchAndSyncRemote() {
# we are in the start directory

pathend=$(awk '{split($0,a,"code"); print a[2]}' <<< "$(pwd)")
serverpath="$pathstart""$pathend"

mkdir -p Transient/results
if [ "$steadyState" = true ]; then
  mkdir -p SteadyState/results
fi

while true; do 
  rsync -avz --partial --exclude 'case.result' --exclude 'report.log' --progress -e ssh $myserver:$serverpath/Transient/results Transient/  
  if [ "$steadyState" = true ]; then
    rsync -avz --partial --exclude 'case.result' --exclude 'report.log' --progress -e ssh $myserver:$serverpath/SteadyState/results SteadyState  
  fi
  sleep 5; 
done
}

# -----------------------------------
# Function solveElmer()
# -----------------------------------

# Elmer workflow
# 1) Create working instance of ElmerGUI and generate sif
# 2) Run the simulation save convergence graph (via gnuplot) 

solveElmer() {



  sim=${simulation//[[:space:]]/}
  printf "\nStarting simulation for ${color}${simulation}${nocolor}\n"

  if [ "$modal" = true ]; then
    sim="Modal"
  fi

  mkdir -p "$sim/results"
  
  cd "$sim"
  
  ln -s -f "$startDir/mesh" "."
  
  if [ "$modal" = true ]; then
    cp "$baseDir/case_modal.sif" "case.sif"
  else 
    cp "$baseDir/case.sif" "case.sif"
    ln -s -f "$startDir/mesh/myprocedures.so" "."
    points="$( python $baseDir/analyze.py --points )"
    points='Save Points (4) = '$points
  fi

  uname -a > results/report.log

  # filling in the variables from config.ini
  fields=(maxiterations simulation outputfile nsmaxiterations ssrelax sstolerance restart nstolerance step intervals outletbc nsoptions elasticsolversettings starttime points outputintervals ymepithelium ymfold other materialsettings) 
  
  for field in ${fields[@]}
  do
    fillIn "$field" "case.sif"
  done

  echo "Starting Elmer Solver..."
  echo "... you may read the log in dir $sim/results/report.log"

  watchAndSync & watcher_pid=$!
  ElmerSolver "case.sif" | tee results/report.log | egrep 'MAIN|ERROR|SS' | tee results/short.log 

  kill $watcher_pid
  wait $watcher_pid 2>/dev/null

  if ls "mesh/case"*".vtu" 1> /dev/null 2>&1; then
    mv "mesh/case"*".vtu" results >> results/report.log 2>&1 
  fi

  if ls "mesh/case.result" 1> /dev/null 2>&1; then
    mv "mesh/case.result" results >> results/report.log 2>&1 
  fi

  echo "Elmer Solver finished"

  cd results
  if ls "case"*".vtu" 1> /dev/null 2>&1; then
    saveAnimation || echo -e "Animation failed."
  else
    echo "There are no data to animate."
  fi
  cd ../..

}


# -----------------------------------
# Function startInfo()
# -----------------------------------

startInfo() {
printf "\n${color}vocalSolve${nocolor}\n-------------\n \n"

}

# -----------------------------------
# Function showProbes()
# -----------------------------------

showProbes() {
  python $baseDir/findpoints.py
}

# -----------------------------------
# Function helpMe()
# -----------------------------------

helpMe() {
echo "How to use vocalSolve:"
echo "1. Before using please install with ./vocalSolve -i"
echo "2. Set options in config.ini and run: vocalSolve [--remote]"
echo -e "\n"
}

# -----------------------------------
# Function generateMesh()
# -----------------------------------

# Generate mesh based on the read parameters

generateMesh() {

  if [ "$skipmesh" = true ]; then
    return 0
  fi

  echo "hdist" $hdist

  if (( $( bc <<< "$hdist <= 0" ) )); then 
    echo "Too small separation between the folds, please set hdist > 0";
    exit; 
  fi

  cp $baseDir/hlasivka-flat.geo $startDir/ # copy the geometry file
  vertShift=$( bc <<< "0.3 - $hdist" )     # define vertical shift

  # filling in the variables from config.ini
  fields=(hdist centralh globallc channellength channelstart meshalgo refine) 
  
  for field in ${fields[@]}
  do
    fillIn "$field" "hlasivka-flat.geo"
  done

  mkdir -p $startDir/mesh
  echo "Generating mesh..."
  uname -a > mesh/report.log
  ~/bin/mygmsh hlasivka-flat.geo - >> mesh/report.log 2>&1

  echo "Converting mesh to Elmer..."
  ElmerGrid 14 2 hlasivka.msh -autoclean -out mesh >> mesh/report.log 2>&1

  echo "Saving screenshot..."
  ~/bin/mygmsh hlasivka.msh $baseDir/saveimg.geo
  mv $baseDir/file.png $startDir/mesh/screenshot.png
  
  cp "$baseDir/myprocedures.f90" "mesh"
  cd mesh
  
  ymax=$( bc <<< "(1.0000 + $hdist )*0.01" )
  echo "ymax " $ymax
  
  fillIn "ymax" "myprocedures.f90"   # fill in the file
  fillIn "vmax" "myprocedures.f90"

  echo -n "\nCompiling the fortran script..."
  elmerf90 "myprocedures.f90" -o "myprocedures.so"
  cd ..
      
  # 
   
  #rm hlasivka.msh
}

# -----------------------------------
# Function checkConfigFile()
# -----------------------------------

# see whether the config file is present

checkConfigFile() {

if [ ! -f config.ini ]; then
   echo "Wrong folder - missing configuration file config.ini"
   exit;
fi

}

# -----------------------------------
# Function updateScript()
# -----------------------------------

# commits the changes and sync

updateScript() {

cd $baseDir
git pull
git add -A .
git commit -m "Updating from the script"
git push

ssh $myserver "cd $pathstart; git pull"
cd $startDir
}


# -----------------------------------
# Function runOnRemote()
# -----------------------------------

# run the script vocalSolve on a distant machine and download the results

runOnRemote() {

startupClean
checkConfigFile

pathend=$(awk '{split($0,a,"code"); print a[2]}' <<< "$(pwd)")
serverpath="$pathstart""$pathend"

# we transfer our config file to the server...
ssh $myserver "mkdir -p $serverpath"
rsync -aze ssh config.ini $myserver:$serverpath/config.ini;

# ... and start watching the results directory for new pieces
mkdir -p Transient/results

if [ "$steadyState" = true ]; then
  mkdir -p SteadyState/results
fi

echo "We shall execute remote script"
ssh -X $myserver "DISPLAY=:0;cd $serverpath;"'PATH="/opt/paraview/bin:$HOME/bin:$PATH";nohup vocalSolve >> report.log 2>&1 &'
echo -e "The remote script has been executed and is running."
echo -e "... see report.log. You can now synchronize calling vocalSolve -s (you may later resume with the same command)."

sleep 5;
rsync -aze ssh $myserver:$serverpath/.proc.id .
echo -e "Number of process on the remote computer: "
procnum=$(cat '.proc.id')
echo -e $procnum
echo -e "You may also run vocalSolve -c to connect to remote and kill $procnum"
}

# -----------------------------------
# Function runLocally()
# -----------------------------------

# run the script vocalSolve locally and save the results to the folders
# 1) Initialization
# 2) Generate mesh
# 3) Get a reasonable stacionary solution (see Elmer wf bellow)
# 4) Develop a time dependent solution (see Elmer wf bellow)


runLocally() {

#startupClean

# for distant version activate Elmer
if [ "$(uname -n)" == "geof40" ]; then 
  source load_elmer8; 
  echo "We are on geof40, the hooks activated"
  echo "The process id on the remote is $$"
  echo "$$" > .proc.id
  color=''
  nocolor=''
else
  echo "We are at home, no hooks necesary"  
fi

generateMesh

# some calculations




# Steady State solution

if [ "$steadyState" = true ]; then
  simulation="SteadyState"
  outputfile='Output File = case.result'
    
  solveElmer
  
  if [ ! -f "$startDir/SteadyState/results/case.result" ]; then
       echo "File case.result was not created in Steady State. Aborting..."
       exit
  fi
  
  restart='Restart File = "case.input"; Restart Position = 0;'

  ln -s -f "$startDir/SteadyState/results/case.result" "$startDir/SteadyState/mesh/case.input"
fi

# Transient solution
simulation=Transient

# Modal analysis

if [ "$modal" = true ]; then
  simulation="Steady State"
fi

solveElmer

}

# -----------------------------------
# Function installThis()
# -----------------------------------

# Install this program locally

installThis() {
  ln -sf "$baseDir/vocalSolve" "$HOME/bin/vocalSolve"
  sudo apt-get install gfortran
  # install elmer via ppa
  # install gmsh from its webpage
}


# -----------------------------------
# Function saveAnimation()
# -----------------------------------

# Convert caseXXXX.vtu in the current directory to video.ogv animation

saveAnimation() {
  echo -e "\nStarting animation..."
  pvbatch --use-offscreen-rendering $baseDir/animation.py
  echo -e "Animation was successfully saved"
}

# -----------------------------------
# Function startupClean()
# -----------------------------------

# clean the directory at startup

startupClean() {
  rm -R Transient SteadyState .proc.id report.log 'case.sif' myprocedures.so hlasivka.msh hlasivka-flat.geo mesh  2> /dev/null
}

# -----------------------------------
# Function connect()
# -----------------------------------

# connect to remote machine directory

connect() {
  pathend=$(awk '{split($0,a,"code"); print a[2]}' <<< "$(pwd)")
  serverpath="$pathstart""$pathend"

  ssh -t $myserver "mkdir -p $serverpath; cd $serverpath; ps aux | grep ElmerSolver | awk '{ print \$2}' | xargs -L1 pwdx; echo 'Your commands:'; bash"
}

# -----------------------------------
# Function analyze()
# -----------------------------------

# connect to remote machine directory

analyze() {
  points
  
  pathend=$(awk '{split($0,a,"code"); print a[2]}' <<< "$(pwd)")
  serverpath="$pathstart""$pathend"

  rsync -avz --partial --progress -e ssh $myserver:$serverpath/Transient/{sensors.dat,sensors.dat.names} Transient/

  python $baseDir/analyze.py --graphs
}


# -----------------------------------
# Function points()
# -----------------------------------

# print IDS of points with probes

points() {
  pathend=$(awk '{split($0,a,"code"); print a[2]}' <<< "$(pwd)")
  serverpath="$pathstart""$pathend"

  mkdir -p mesh

  rsync -avz --partial --progress -e ssh $myserver:$serverpath/Transient/mesh/{mesh.nodes,mesh.boundary} mesh/  
  
  python $baseDir/analyze.py --points
}

# -----------------------------------
# Function listps()
# -----------------------------------

# list the simulations running on the machine

listps() {
  ps aux | grep ElmerSolver | awk '{ print $2}' | xargs -L1 pwdx
}
