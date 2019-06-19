import clr
import sys
import thread

#sys.path.append(R'C:\Program Files (x86)\Anite\LogViewer\ALV2')
# clr.FindAssembly("Anite.Logging.Server.Interface.VS2015")
clr.AddReference("Anite.Logging.Server.Interface.VS2015")

from System import *
from System.Collections.Generic import *
from Anite import *
from Anite.Logging.Server.API import *

logFileName = R"C:\Data\Unisoc\ALSI\AlsiNewSamples\AlsiSamples\TestFiles\MAC\170629_VDT.alf"
filterFileName = R"C:\Data\Unisoc\ALSI\AlsiNewSamples\AlsiSamples\TestFiles\MAC\MAC_SummaryReports.alvf"

def Connected(sender, event):
    Alsi.Logger.Info("Plugin: Connected event Connected")

def Disconnected(sender, event):
    Alsi.Logger.Info("Plugin: Disconnected event Connected")

def FetchAllRecords():
   #progress = 0
   totalRecordsCount = 0
   lastPercentRecords = 0
   for progress in range(0,100):
       progress = progress + 1
       percentRecords = (_viewRecordCount * progress) / 100
       requestedRecords = percentRecords - lastPercentRecords
       if requestedRecords != 0:
           r_Value = clr.Reference[List[IDecodedRecord2]]()
           # 获取Log的内容
           ret = _logFileAnalysis.GetDecodedRecordList(r_Value, _selectedViewId, lastPercentRecords, requestedRecords)
           records = r_Value.Value
           if Alsi.StatusCode.Ok == ret.Code:
               if None != records:
                   totalRecordsCount = totalRecordsCount + records.Count
                   # 可以在这里decode log信息 以及进一步的处理，比如：保存到文件，获取自己关心的内容等
                   print records
       lastPercentRecords = percentRecords;


if __name__ == "__main__":   
    # 创建 Log server的实例
    _alsi = AniteLoggingServerInterface()
    _alsi = clr.Convert(_alsi, IAniteLoggingServer2)
    print(_alsi)
    if _alsi is None:
        print "object is null"

    print _alsi.GetVersion()
    print _alsi.GetBuiltInAlsiSchemaVersion.ToString()
    _connection = _alsi.Connection
    _connection = clr.Convert(_connection, IConnection)
    _connection.OnConnected += Connected
    _connection.OnDisconnected += Disconnected
    print(_connection)
    # 获取Log Server的信息
    status = _alsi.CheckLoggingServerCompatability()
    print status
    if status.Code == Alsi.StatusCode.Ok:
        print "Anite Logging Server Version: " + status.Message
    # 连接到Server
    if _connection.IsConnected() == False:
        status = _connection.Connect()
        if status.Code == Alsi.StatusCode.Ok:
            print "connect OK"

    _logFileAnalysis = _alsi.LogFileAnalysis4(_connection)
    print(_logFileAnalysis)
    if _logFileAnalysis is None:
        print "object is null"
    # 打开Log 文件
    status = _logFileAnalysis.OpenLogFile(logFileName)

    # 元组的第一个保存status
    if Alsi.StatusCode.Ok != status[0].Code:
        print "Open File failed."

    # 元组的第二个保存record count
    _recordsCount = status[1] 

    # 加载Filter文件
    status = _logFileAnalysis.CreateLogFileView(filterFileName, None)
    if Alsi.StatusCode.Ok != status[0].Code:
        print "Create Log File View failed."

    # 返回值第二个保存id
    _selectedViewId = status[1]
    _viewRecordCount = _recordsCountAfterFilter = status[2]

    FetchAllRecords()

    # 关闭Log文件
    status = _logFileAnalysis.CloseLogFile()
    if Alsi.StatusCode.Ok != status.Code:
        print "Error Code = " + status.Code.ToString() 
    # 断开连接
    _connection.Disconnect()