import Collapse from '@mui/material/Collapse';
import * as React from 'react';

export const AccordionCard = (props) => {
  const [open, setOpen] = React.useState(false);

  const handleChange = () => {
    setOpen((prev) => !prev);
  };

  return (
    <div className="mb-4 w-full">
      <button onClick={handleChange}
        className="bg-custom-secondary rounded-t-md px-4 py-2 font-bold w-full text-left shadow-md flex flex-row cursor-pointer"
      >
        {props.icon}{props.title}
      </button>
      <div className="flex">
        <Collapse in={open} timeout="auto" className="w-full" unmountOnExit>
          <div className='bg-white rounded-b-md shadow-sm px-4 pt-2 pb-3 transition duration-500 ease-in-out w-full'>
            {props.content}
          </div>
        </Collapse>
      </div>
    </div>
  );
}
