import React, { useMemo, useState } from "react";
import {
  MaterialReactTable,
  MRT_ColumnDef,
  useMaterialReactTable
} from "material-react-table";
import { Box, Button, Chip, Stack } from "@mui/material";


interface AudioData {
    name: string;
    tags: string[];
    dateAdded: string;
    evaluated: string;
    rating: number;
}




export default function TableTest({ audioData }: { audioData: AudioData[] }) {

    // For filtering
    const tagOptions = useMemo(() => {
        const allTags = new Set<string>();
        audioData.forEach((row) => row.tags.forEach((tag) => allTags.add(tag)));
        return Array.from(allTags);
      }, [audioData]);


  // Define columns with proper typing
  const columns = useMemo<MRT_ColumnDef<AudioData>[]>(
    () => [
      {
        accessorKey: "name", // Recommended way
        header: "Audio Clips",
        muiTableHeadCellProps: { sx: { color: "black" } },
        Cell: ({ renderedCellValue }) => <strong>{renderedCellValue}</strong>
      },
      {
        accessorKey: "tags",
        header: "Tags",
        muiTableBodyCellProps: {
          sx: {
            whiteSpace: 'normal',
            verticalAlign: 'top',
          },
        },

        
        filterVariant: 'multi-select',
        filterSelectOptions: tagOptions,
        Cell: ({ cell }) => {
          const tags = cell.getValue<string[]>();
          const [expanded, setExpanded] = useState(false);
          const tagLimit = 3;
      
          const displayTags = expanded ? tags : tags.slice(0, tagLimit);
          const hasMore = tags.length > tagLimit;
      
          return (
            <Box>
              <Stack
                direction="row"
                flexWrap="wrap"
                gap={1}
              >
                {displayTags.map((tag: string, index: number) => (
                  <Chip
                    key={index}
                    label={tag}
                    size="small"
                    sx={{
                      backgroundColor: '#e0f7fa',
                      color: '#00796b',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                    }}
                  />
                ))}
              </Stack>
      
              {hasMore && (
                <Button
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  sx={{
                    mt: 1,
                    minHeight: 'unset',
                    padding: 0,
                    textTransform: 'none',
                    fontSize: '0.75rem',
                  }}
                >
                  {expanded ? 'Show less' : `+${tags.length - tagLimit} more`}
                </Button>
              )}
            </Box>
          );
        },
      },
      {
        accessorKey: "dateAdded", // Recommended way
        header: "Date Added",
        muiTableHeadCellProps: { sx: { color: "black" } },
        Cell: ({ renderedCellValue }) => <strong>{renderedCellValue}</strong>
      },
      {
        accessorKey: "evaluated", // Recommended way
        header: "Evaluated",
        muiTableHeadCellProps: { sx: { color: "black" } },
        Cell: ({ renderedCellValue }) => <strong>{renderedCellValue}</strong>
      },
      {
        accessorKey: "rating", // Recommended way
        header: "Rating",
        muiTableHeadCellProps: { sx: { color: "black" } },
        Cell: ({ renderedCellValue }) => <strong>{renderedCellValue}</strong>
      },
    ],
    [audioData, tagOptions] // Add tagOptions to dependencies
  );

  const table = useMaterialReactTable({
    data: audioData,
    columns,
    enableFacetedValues: true,
    // renderEmptyRowsFallback: ({ }) => (
    //     <span>Customized No Rows Overlay</span>
    // ),
    // enablePagination: false,
    renderBottomToolbar: false,
    enableFullScreenToggle: false,
    initialState: {density:'compact', showColumnFilters: true},
    muiTableBodyCellProps: {sx: {whiteSpace: 'normal', verticalAlign: 'top',    }},
    enableDensityToggle: false,
    enableExpanding: true,
    // getRowCanExpand: () => true,
    // renderDetailPanel: ({ row }) => {
    //     const tags = row.original.tags;
    //     return (
    //     <Box sx={{ padding: 2 }}>
    //         <Stack direction="row" spacing={1} flexWrap="wrap">
    //         {tags.map((tag, index) => (
    //             <Chip key={index} label={tag} size="small"
    //             sx={{ bgcolor: "#e0f7fa", color: "#00796b", fontWeight: "bold" }}/>
    //         ))}
    //         </Stack>
    //     </Box>
    //     );
    // },
  });

  return <MaterialReactTable table={table} />;
}