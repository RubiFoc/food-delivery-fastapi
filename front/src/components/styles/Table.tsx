import { Button } from "@/components/ui/button"

interface TableProps {
  headers: string[]
  data: any[]
  onEdit: (item: any) => void
  onDelete: (item: any) => void
}

export function Table({ headers, data, onEdit, onDelete }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white">
        <thead>
          <tr className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
            {headers.map((header, index) => (
              <th key={index} className="py-3 px-6 text-left">{header}</th>
            ))}
            <th className="py-3 px-6 text-center">Actions</th>
          </tr>
        </thead>
        <tbody className="text-gray-600 text-sm font-light">
          {data.map((item, index) => (
            <tr key={index} className="border-b border-gray-200 hover:bg-gray-100">
              {headers.map((header, headerIndex) => (
                <td key={headerIndex} className="py-3 px-6 text-left whitespace-nowrap">
                  {item[header.toLowerCase()]}
                </td>
              ))}
              <td className="py-3 px-6 text-center">
                <div className="flex item-center justify-center">
                  <Button onClick={() => onEdit(item)} className="mr-2">Edit</Button>
                  <Button onClick={() => onDelete(item)} variant="destructive">Delete</Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

