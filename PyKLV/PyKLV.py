import clr
import os
import sys
import datetime

sys.path.append(R'C:\Program Files (x86)\Anite\LogViewer\ALV2')
sys.path.append(R'C:\Program Files (x86)\Anite\LogViewer\ALV2\Common')
# clr.FindAssembly("Anite.Logging.Server.Interface.VS2015")
clr.AddReference("Anite.Logging.Server.Interface.VS2015")
#clr.AddReference("System.Reflection.RuntimeAssembly")
clr.AddReference('System.Collections')
#clr.AddReference('Microsoft.Practices.Prism')
clr.AddReference('Anite.Logs')
clr.AddReference('Anite.Logs.Common')
    
from System import *
from System.Runtime import *
from System.Reflection import *
from System.Collections.Generic import *
from Anite import *
from Anite.Logs import *
from Anite.Logging.Server.API import *

global _validatedCount
_validatedCount = 0

logFileName = R"C:\Data\Unisoc\ALSI\AlsiNewSamples\AlsiSamples\TestFiles\MAC\170629_VDT.alf"
filterFileName = R"C:\Data\Unisoc\ALSI\AlsiNewSamples\AlsiSamples\TestFiles\MAC\MAC_SummaryReports.alvf"

def Connected(sender, event):
    Alsi.Logger.Info("Plugin: Connected event Connected")

def Disconnected(sender, event):
    Alsi.Logger.Info("Plugin: Disconnected event Connected")

def FetchAllRecords():
    results = ""
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
                   results = results + ProcessFetchedRecords(records)
       lastPercentRecords = percentRecords;
    # 保存结果到文件
    nowTime=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    f = open(os.path.abspath(os.curdir) + "\\Log\\Log-" + nowTime + ".txt", "w")
    f.write(results)
    f.close()

def ProcessFetchedRecords(records):
    global _validatedCount
    for record in records:
        #parents = clr.Reference[List[IRecordRelationship]]()
        parents = List[IRecordRelationship]()
        ret = _logFileAnalysis.GetRecordParents(parents, _selectedViewId, record.GlobalIndex)
        i = 0
        if parents.Count > 0:
            print("Record " + record.RecordName +", Global index " + record.GlobalIndex + " has " + parents.Count + " parents:")
            for parent in parents:
                decRecord = clr.Reference[List[IDecodedRecord2]]()
                ret = _logFileAnalysis.GetDecodedRecordList(decRecord, _selectedViewId, parent.LocalIndex, 1)
                if Alsi.StatusCode.Ok == ret[0].Code:
                    print("  Parent Record " + i + ", GI = " + parent.GlobalIndex + ", LI = " + parent.LocalIndex + ", isHidden = " + parent.IsHidden + ", "+ decRecord[0].RecordName )
                else:
                    print("  Parent Record " + i + ", GI = " + parent.GlobalIndex + ", LI = " + parent.LocalIndex + ", isHidden = " + parent.IsHidden + ", Failed to decode related record ")
                i = i + 1

        children = List[IRecordRelationship]()
        ret = _logFileAnalysis.GetRecordChildren(children, _selectedViewId, record.GlobalIndex)
        i = 0
        if children.Count > 0:
            print("Record " + record.RecordName +", Global index " + record.GlobalIndex + " has " + parents.Count + " children:")
            for child in children:
                decRecord = clr.Reference[List[IDecodedRecord2]]()
                ret = _logFileAnalysis.GetDecodedRecordList(decRecord, _selectedViewId, parent.LocalIndex, 1)
                if Alsi.StatusCode.Ok == ret[0].Code:
                    print("  Child Record " + i + ", GI = " + parent.GlobalIndex + ", LI = " + parent.LocalIndex + ", isHidden = " + parent.IsHidden + ", "+ decRecord[0].RecordName )
                else:
                    print("  Child Record " + i + ", GI = " + parent.GlobalIndex + ", LI = " + parent.LocalIndex + ", isHidden = " + parent.IsHidden + ", Failed to decode related record ")
                i = i + 1

        results = CreateRecordHeaderText(record) + "\n"
        results = results + CreateRecordPayloadText(record) + "\n"
        validator = AlsiValidator()
        status = validator.LogRecord(record)
        if status.Code == Alsi.StatusCode.Ok:
            _validatedCount = _validatedCount + 1
            results = results + "\n" + str(record.RecordName) + "\nRecord Validated - OK\n"
        else:
            results = results + "\n" + str(record.RecordName) + "\nRecord Validated - Fail:" + str(status.Message) + "\n"

        deserialiser = AlsiDeserialiser()
        ret = deserialiser.LogRecord(record)
        if Alsi.StatusCode.Ok == ret[0].Code:
            results = results + CreateRecordText(ret[1]) + "\n"
        
        return results

def CreateRecordHeaderText(record):
    results = ""
    if record.XmlPayLoad.Contains("cause=\"rcInfoError\"") == False:
        if record is not None:
            results = results + "RECORD DETAILS:\n"
            results = results + "\n  local index         = " + str(record.LocalIndex)
            results = results + "\n  global index        = " + str(record.GlobalIndex)
            results = results + "\n  error code          = " + str(record.ErrorCode)
            results = results + "\n  error message       = " + str(record.ErrorMessage)
            results = results + "\n  record name         = " + str(record.RecordName)
            results = results + "\n  record type         = " + str(record.RecordType)
            results = results + "\n  record id           = " + str(record.RecordId)
            results = results + "\n  record version id   = " + str(record.RecordVersionId)
            results = results + "\n  source              = " + str(record.Source)
            results = results + "\n  destination         = " + str(record.Destination)
            results = results + "\n  frame number        = " + str(record.FrameNumber)
            results = results + "\n  single line summary = " + str(record.SingleLineSummary)
            results = results + "\n  summary             = " + str(record.Summary)
            results = results + "\n  overview            = " + str(record.Overview)
            results = results + "\n PROTOCOL INFO:"
            results = results + "\n    protocol name           = " + str(record.ProtocolInfo.Name)
            results = results + "\n    protocol id             = " + str(record.ProtocolInfo.Id)
            results = results + "\n    protocol version name   = " + str(record.ProtocolInfo.VersionName)
            results = results + "\n    protocol version id     = " + str(record.ProtocolInfo.VersionId)
            results = results + "\n    protocol decoder path   = " + str(record.ProtocolInfo.DecoderPath)
            results = results + "\n  TIMESTAMP INFO:"
            results = results + "\n    local date               = " + str(record.TimeStampInfo.LocalDate)
            results = results + "\n    local time               = " + str(record.TimeStampInfo.LocalTime)
            results = results + "\n    delta time               = " + str(record.TimeStampInfo.DeltaTime)
            results = results + "\n    short delta time         = " + str(record.TimeStampInfo.ShortDeltaTime)
            results = results + "\n    has simulated delta time = " + str(record.TimeStampInfo.HasSimulatedDeltaTime)
            results = results + "\n    simulated delta time     = " + str(record.TimeStampInfo.SimulatedDeltaTime)
            results = results + "\n  RELATIONSHIP:"
            results = results + "\n    has Parent = " + str(record.HasParents)

    return results

def CreateRecordPayloadText(record):
    results = ""
    if record.XmlPayLoad.Contains("cause=\"rcInfoError\"") == False:
        if record is not None:
            results = "XML PAYLOAD:\n"
            results = results + str(record.XmlPayLoad) + "\n"
            results = results + str(record.XmlPayLoadElement) + "\n"
    return results

def CreateRecordText(record):
    results = ""
    if record.cause != TRecordCause.rcInfoError:
        pass
    else:
        results = results + "DE-SERIALISED PAYLOAD:"
        if None != record.schema:
            results = results + "\n  schema              = " + str(record.schema)

        results = results + "\n  cause specified     = " + str(record.causeSpecified)
        results = results + "\n  cause               = " + str(record.cause)

        if None != record.Frame:
            results = results + "\n  frame               = " + str(record.Frame)
        if None != record.Summary:
            results = results + "\n  summary               = " + str(record.Summary)
        if None != record.Overview:
            results = results + "\n  overview               = " + str(record.Overview)

        if None != record.SourceCodeReference:
            results = results + "\n  sourcecode reference line specified      = " + str(record.SourceCodeReference.lineSpecified)
            results = results + "\n  sourcecode reference line                = " + str(record.SourceCodeReference.line)
            results = results + "\n  sourcecode reference line description    = " + str(record.SourceCodeReference.description)
            results = results + "\n  sourcecode reference line path           = " + str(record.SourceCodeReference.path)

        if None != record.Field:
            for field in record.Field:
                if None != field:
                    results = results + "\n  field name = " + str(field.name)
                    for obj in field.Items:
                        if obj is TValue:
                            value = clr.Convert(obj, TValue)
                            if None != value.Text:
                                for svalue in value.Text:
                                    results = results + "\n    value = " + str(svalue)
                            if None != value.i:
                                index = 0
                                for svalue in value.i:
                                    results = results + "\n    value[" + str(index) + "] = " + str(svalue)
                                    index = index + 1
                        elif obj is TField:
                            innerField = clr.Convert(obj, TField)
                            results = results + "\n    field name = " + str(innerField.name)
                            if innerField.decodeSpecified:
                                results = results + "\n        found decode attribute = " + str(innerField.decode)
    return results

if __name__ == "__main__":   
    # 创建 Log server的实例
    _alsi = AniteLoggingServerInterface()
    _alsi = clr.Convert(_alsi, IAniteLoggingServer2)
    print(_alsi)
    if _alsi is None:
        print ("object is null")

    print (_alsi.GetVersion())
    print (_alsi.GetBuiltInAlsiSchemaVersion.ToString())
    _connection = _alsi.Connection
    _connection = clr.Convert(_connection, IConnection)
    _connection.OnConnected += Connected
    _connection.OnDisconnected += Disconnected
    print(_connection)
    # 获取Log Server的信息
    status = _alsi.CheckLoggingServerCompatability()
    print (status)
    if status.Code == Alsi.StatusCode.Ok:
        print ("Anite Logging Server Version: " + status.Message)
    # 连接到Server
    if _connection.IsConnected() == False:
        status = _connection.Connect()
        if status.Code == Alsi.StatusCode.Ok:
            print ("connect OK")

    #_loggingServerInterface = AniteLoggingServerInterface()
    #print(_loggingServerInterface)
    #if _alsi is None:
    #    print "object is null"
    #_logFileAnalysis = _loggingServerInterface.LogFileAnalysis4(_connection)
    _logFileAnalysis = _alsi.LogFileAnalysis4(_connection)
    print(_logFileAnalysis)
    if _logFileAnalysis is None:
        print ("object is null")
    # 打开Log 文件
    status = _logFileAnalysis.OpenLogFile(logFileName)

    # 元组的第一个保存status
    if Alsi.StatusCode.Ok != status[0].Code:
        print ("Open File failed.")

    # 元组的第二个保存record count
    _recordsCount = status[1] 

    # 加载Filter文件
    status = _logFileAnalysis.CreateLogFileView(filterFileName, None)
    if Alsi.StatusCode.Ok != status[0].Code:
        print ("Create Log File View failed.")

    # 返回值第二个保存id
    _selectedViewId = status[1]
    _viewRecordCount = _recordsCountAfterFilter = status[2]
	# 抓取并解析Log
    FetchAllRecords()

    # 关闭Log文件
    status = _logFileAnalysis.CloseLogFile()
    if Alsi.StatusCode.Ok != status.Code:
        print ("Error Code = " + status.Code.ToString())
    # 断开连接
    _connection.Disconnect()