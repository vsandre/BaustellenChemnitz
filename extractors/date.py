#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, re

class DateExtractionException(Exception):
  pass

def extract(dateString):
  """
    Return a dict with following keys: since, until, note(optional)

    some examples can be found in 'date.py.test'
  """

  def intyear(yearstring):
    """
      return a valid integer even if nothing is found in the date string
    """
    year = int(yearstring if (len(yearstring)>0) else 1)
    return year if (year>0) else 1

  def checkDate(data_to_check):
    """
      Check if date or time periode is valid
    """
    #now = datetime.datetime.now()
    today = datetime.date.today()
    century = (today.year // 100) * 100

    if ((data_to_check['until'] != None) and (data_to_check['since'] != None)):
      if (data_to_check['since'].year < 100) and (data_to_check['since'].year != 1):
        data_to_check['since'] = data_to_check['since'].replace(year=data_to_check['since'].year + century);
      if (data_to_check['until'].year < 100) and (data_to_check['until'].year != 1):
        data_to_check['until'] = data_to_check['until'].replace(year=data_to_check['until'].year + century);

      if (data_to_check['until'].year == 1):
        if (abs((data_to_check['until'].replace(year=today.year) - today).days) < abs(today - data_to_check['until'].replace(year=today.year-1)).days):
          data_to_check['until'] = data_to_check['until'].replace(year=today.year);
        else:
          data_to_check['until'] = data_to_check['until'].replace(year=today.year-1);

      if (data_to_check['since'].year == 1) and (data_to_check['until'].year != 1):
        if (data_to_check['since'].month <= data_to_check['until'].month):
          data_to_check['since'] = data_to_check['since'].replace(year=data_to_check['until'].year);
        else:
          data_to_check['since'] = data_to_check['since'].replace(year=data_to_check['until'].year-1);

      if (data_to_check['since'] > data_to_check['until']):
        data_to_check['until'] = data_to_check['until'].replace(year=data_to_check['until'].year+1);

    if (data_to_check['until'] == None):
      if (data_to_check['since'].year < 100) and (data_to_check['since'].year != 1):
        data_to_check['since'] = data_to_check['since'].replace(year=data_to_check['since'].year + century);
      if (data_to_check['since'].year == 1):
        data_to_check['since'] = data_to_check['since'].replace(year=today.year);

    if (data_to_check['since'] == None):
      if (data_to_check['until'].year < 100) and (data_to_check['until'].year != 1):
        data_to_check['until'] = data_to_check['until'].replace(year=data_to_check['until'].year + century);
      if (data_to_check['until'].year == 1):
        data_to_check['until'] = data_to_check['until'].replace(year=today.year);

    return data_to_check
  #end of: def checkDate(data_to_check)

  data = {}
  dateRegex = '(\d{1,2})\.(\d{1,2})\.(\d{0,4})'
  specificDate = re.match('^(am)?\s*' + dateRegex  + '$', dateString)
  if specificDate:
    tmp = specificDate.groups()
    date = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    data['since'] = date
    data['until'] = date
    checkDate(data)
    return data

  fromToDate = re.match('^(von|ab|seit)?\s*' + dateRegex + '\s*(bis|-)\s*' + dateRegex + ',?\s*(.*)$', dateString)
  if fromToDate:
    tmp = fromToDate.groups()
    sinceDate = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    untilDate = datetime.date(
      intyear(tmp[7]),
      int(tmp[6]),
      int(tmp[5])
    )
    data['since'] = sinceDate
    data['until'] = untilDate
    checkDate(data)
    return data

  fromDate = re.match('^(ab|seit)?\s*' + dateRegex + '$', dateString)
  if fromDate:
    tmp = fromDate.groups()
    date = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    data['since'] = date
    data['until'] = None
    checkDate(data)
    return data

  untilDate = re.match('^(bis)?\s*' + dateRegex + '$', dateString)
  if untilDate:
    tmp = untilDate.groups()
    date = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    data['since'] = None
    data['until'] = date
    checkDate(data)
    return data

  timerangeRegex = '(\d{1,2}[\.\:]\d{1,2}\s*-\s*\d{1,2}[\.\:]\d{1,2}\s*(Uhr))?'
  specificDateWithTimerange = re.match('^(am)?\s*' + dateRegex  + '\s*,\s*' + timerangeRegex + '$', dateString)
  if specificDateWithTimerange:
    tmp = specificDateWithTimerange.groups()
    date = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    data['since'] = date
    data['until'] = date
    data['note'] = tmp[4]
    checkDate(data)
    return data

  middleRegex = '((Anfang|Mitte|Ende)?)'
  monthRegex = '(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)?'

  def estimatedDate(year,month,middle,start):
    if   (month == 'Januar'):    monthN =  1;
    elif (month == 'Februar'):   monthN =  2;
    elif (month == 'März'):      monthN =  3;
    elif (month == 'April'):     monthN =  4;
    elif (month == 'Mai'):       monthN =  5;
    elif (month == 'Juni'):      monthN =  6;
    elif (month == 'Juli'):      monthN =  7;
    elif (month == 'August'):    monthN =  8;
    elif (month == 'September'): monthN =  9;
    elif (month == 'Oktober'):   monthN = 10;
    elif (month == 'November'):  monthN = 11;
    elif (month == 'Dezember'):  monthN = 12;
    else: monthN = 0;

    days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (monthN != 0): lastDay = days_per_month[monthN - 1];
    else: lastDay = 28;

    if (monthN != 0):
      if   (middle == 'Ende'):   day = lastDay;
      elif (middle == 'Mitte'):  day = 15;
      elif (middle == 'Anfang'): day = 1;
      else:
        if start: day = 1;
        else: day = lastDay
    else:
      if   (middle == 'Ende'):   day = 31; monthN = 12;
      elif (middle == 'Mitte'):  day =  1; monthN =  7;
      elif (middle == 'Anfang'): day =  1; monthN =  1;
      else:
        if start:                day =  1; monthN =  1;
        else:                    day = 31; monthN = 12;

    return datetime.date(year, monthN, day)

  untilEstimatedDate = re.match('^(ab|seit)?\s*' + dateRegex + '\s*bis voraussichtlich\s*' + middleRegex + '\s*'+ monthRegex + '\s*(\d{0,4})(.*)$', dateString)
  if untilEstimatedDate:
    tmp = untilEstimatedDate.groups()
    sinceDate = datetime.date(
      intyear(tmp[3]),
      int(tmp[2]),
      int(tmp[1])
    )
    untilDate = estimatedDate(intyear(tmp[7]),tmp[6],tmp[5],False)
    data['since'] = sinceDate
    data['until'] = untilDate
    data['note'] = 'voraussichtliches Enddatum'
    checkDate(data)
    return data

  sinceEstimatedDate = re.match('^voraussichtlich ab\s*' + middleRegex + '\s*'+ monthRegex + '\s*(\d{0,4})\s*bis\s*' + dateRegex + '$', dateString)
  if sinceEstimatedDate:
    tmp = sinceEstimatedDate.groups()
    sinceDate = estimatedDate(intyear(tmp[3]),tmp[2],tmp[1],True)
    untilDate = datetime.date(
      intyear(tmp[6]),
      int(tmp[5]),
      int(tmp[4])
    )
    data['since'] = sinceDate
    data['until'] = untilDate
    data['note'] = 'voraussichtliches Startdatum'
    checkDate(data)
    return data

  raise DateExtractionException(dateString)

if __name__ == "__main__":
  import doctest
  doctest.testfile("date.py.test")
