# startupAction
This plugin can be used to start indigo actions at startup of indigo

At startup this plugin will check if cpu time used by process IndigoServer
  is less than x[secs] (defined below)
  This is used to check if indigo has just started

if yes: execute action groups 1,2,3 after defined individual delays
        with the individual delays you can sequence the actions
        delay3 &gt;= delay2 &gt;= delay1

then: do nothing, wait until plugin is disabled or indigo shuts down

It does nothing else.

If a parameter is changed, the plugin will restart
   and execute the requested actions after restart if conditions are met
