/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
/*                                 _ooOoo_                                   */
/*                                o8888888o                                  */
/*                                88" . "88                                  */
/*                                (| -_- |)                                  */
/*                                O\  =  /O                                  */
/*                             ____/`---'\____                               */
/*                           .'  \\|     |//  `.                             */
/*                          /  \\|||  :  |||//  \                            */
/*                         /  _||||| -:- |||||-  \                           */
/*                         |   | \\\  -  /// |   |                           */
/*                         | \_|  ''\---/''  |   |                           */
/*                         \  .-\__  `-`  ___/-. /                           */
/*                       ___`. .'  /--.--\  `. . __                          */
/*                    ."" '< `.___\_<|>_/___.'  >'"".                        */
/*                   | | :  `- \`.;`\ _ /`;.`/ - ` : | |                     */
/*                   \  \ `-.   \_ __\ /__ _/   .-` /  /                     */
/*              ======`-.____`-.___\_____/___.-`____.-'======                */
/*                                 `=---='                                   */
/*              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                */
/*                       佛祖保佑       永無bug                              */
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */
#include "log.h"

LOG::LOG(){
}

LOG::LOG(std::string _file_path){
    m_file_path = _file_path;
}

LOG::LOG(std::string _file_path, std::string _service_name){
    m_file_path = _file_path;
    m_service_name = _service_name;
}

void LOG::write(std::string msg){
    time_t rawtime;
    time(&rawtime);
    struct tm *timeinfo = localtime(&rawtime);

    std::ofstream ofs(m_file_path, std::ios::app);
    /* time */
    ofs << "[" 
        << timeinfo->tm_year + 1990 << "/"
        << std::setfill('0') << std::setw(2) << timeinfo->tm_mon + 1 << "/"
        << std::setfill('0') << std::setw(2) << timeinfo->tm_mday << " "
        << std::setfill('0') << std::setw(2) << timeinfo->tm_hour << ":"
        << std::setfill('0') << std::setw(2) << timeinfo->tm_min << ":"
        << std::setfill('0') << std::setw(2) << timeinfo->tm_sec
        << "] ";
    /* pid */
    ofs  << "[" << std::setw(5) << getpid() << "] ";
    /* service_name */
    //if(m_service_name.size())
    //    ofs  << "[" << m_service_name << "] ";
    /* msg */
    ofs << msg << std::endl;
    ofs.close();
}
