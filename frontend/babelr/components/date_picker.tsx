import * as React from 'react';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
// import TextField from '@mui/material/TextField';
import dayjs, { Dayjs } from 'dayjs';
import { useState } from 'react';

export default function DatePickerWrapper() {
    const [value, setValue] = useState<Dayjs | null>(dayjs());
  
    return (
      <>
        <DatePicker
          label=""
          value={value}
          onChange={(newValue) => setValue(newValue)}
        />
        <input
          type="hidden"
          name="dob"
          value={value ? value.format('YYYY-MM-DD') : ''}
        />
      </>
    );
  }