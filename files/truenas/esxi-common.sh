################################################################################
################################################################################
#
# Common code for ESXi support
#
################################################################################
################################################################################

# https://github.com/Spearfoot/utility-scripts-for-freenas-and-vmware-esxi

###############################
# Define variables used later #
###############################

# user and host:

esxiuser=""
esxihost=""

# Record keeping:

totalvms=0
totalvmsshutdown=0
totalvmspowereddown=0

##########################################################
# Edit these settings to suit your needs and environment #
##########################################################

# Test flag: set to 1 to prevent the script from shutting VM guests down.
dryrun=0

# waitretries determines how many times the script will loop while attempting to power down a VM.
# waitdelay specifies how many seconds to sleep during each loop.

waitretries=30
waitdelay=6

# maxwait is the product of waitretries and waitdelay, i.e., the total number of seconds we will
# wait before gracelessly forcing the power off.

maxwait=$((waitretries*waitdelay))

# For tests, force the retry max count to 1
if [ $dryrun -ne 0 ]; then
  waitretries=1
fi

################################################################################
#
# Function to shut down a guest virtual machine
#
################################################################################

shutdown_guest_vm()
{
  l_try=0

  ssh "${esxiuser}"@"${esxihost}" vim-cmd vmsvc/power.getstate $1 | grep -i "off" > /dev/null 2<&1
  l_status=$?

#  printf "VM [%s] status=[%s]\n" "$1" "${l_status}"

  if [ $l_status -eq 0 ]; then
    echo "Guest VM ID $1 already powered down..."
  else
    while [ $l_try -lt $waitretries ] && [ $l_status -ne 0 ]; do
      l_try=$((l_try+1))
      if [ $dryrun -ne 0 ]; then
        echo "TEST MODE: Would issue shutdown command and wait ${waitdelay} seconds for guest VM ID $1 to shutdown (attempt $l_try of $waitretries)..."
      else
        ssh "${esxiuser}"@"${esxihost}" vim-cmd vmsvc/power.shutdown $1 > /dev/null 2<&1
        echo "Waiting ${waitdelay} seconds for guest VM ID $1 to shutdown (attempt $l_try of $waitretries)..."
        sleep $waitdelay
        ssh "${esxiuser}"@"${esxihost}" vim-cmd vmsvc/power.getstate $1 | grep -i "off" > /dev/null 2<&1
        l_status=$?
#	printf "VM [%s] status=[%s] try=[%s]\n" "$1" "${l_status}" "${l_try}"
      fi
    done
    if [ $l_status -eq 0 ]; then
      echo "Shutdown sucessful on attempt ${l_try}..."
      totalvmsshutdown=$((totalvmsshutdown + 1))
    else
      if [ $dryrun -ne 0 ]; then
        echo "TEST MODE: Unable to gracefully shutdown guest VM ID $1, would force power off and wait ${waitdelay} seconds before checking status."
      else
        echo "Unable to gracefully shutdown guest VM ID $1... forcing power off."
        ssh "${esxiuser}"@"${esxihost}" vim-cmd vmsvc/power.off $1 > /dev/null 2<&1
        sleep $waitdelay
      fi
      ssh "${esxiuser}"@"${esxihost}" vim-cmd vmsvc/power.getstate $1 | grep -i "off" > /dev/null 2<&1
      l_status=$?
#      printf "VM [%s] status=[%s]\n" "$1" "${l_status}"
      if [ $l_status -eq 0 ]; then
        totalvmspowereddown=$((totalvmspowereddown + 1))
      fi
    fi
  fi
}
